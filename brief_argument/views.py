import re
import os
import json
import openai
from django.db.models import Func, Value, FloatField, Count, Max, TextField, Prefetch
from django.contrib.postgres.fields import ArrayField
from django.db.models import Q
from django.db.models.functions import Cast
from django.http import HttpResponseRedirect
from django.middleware.csrf import get_token
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from pgvector.django import CosineDistance

from brief_argument.scraper2 import run_playwright
from .models import (
    Argument,
    Case,
    CaseNote,
    Caseparagraph,
    Legal_Memorandum,
    AIB_EXAM,
    HulsburyLawBooks,
    StatementEmbeddings,
    RelevantCitationsPassage,
    CoCounsel,
)
from case_history.models import LegalSearchHistory
from case_history.models import CaseHistory
from .serializers import (
    ArgumentSerializer,
    LegalMemorandumSerializer,
    AIBExamSerializer,
    HulsburyLawBooksSerializer,
    StatementEmbeddingsSerializer,
    RelevantCitationsPassageSerializer,
)
from .utils import (
    decision_value,
    get_case_notes_and_ratio_para,
    get_step_1_input_part2,
    get_step_2_input_part2,
    get_step_3_input_with_lr,
    get_step_3_input_without_lr,
    get_step_4_input_part2,
    get_step_5_input_part2,
    get_top_cases,
    perplexity_scrape,
    perplexity_scrape_selenium,
    send_legal_memo_detail,
    aib_exam__step_1_input,
    aib_exam_step_2_input,
    relevent_topics_input_generator,
    send_aib_mail,
    step2_setup,
    step_2_output_formatter,
    step_3_input_part2,
)


class ArgumentViewSet(viewsets.ModelViewSet):
    queryset = Argument.objects.all()
    serializer_class = ArgumentSerializer

    def create(self, request, *args, **kwargs):
        bulk_update = []
        for analysis in request.data.get("detailed_analysis"):
            formatted_analysis = re.search(
                r"&lt;subsection&gt;(.*?)&lt;\/subsection&gt;",
                analysis["detailed_content"],
                re.DOTALL,
            ).group(1)
            formatted_analysis = formatted_analysis.replace("|$|", "")
            bulk_update.append(
                Argument(id=analysis["id"], detailed_content=formatted_analysis)
            )
        Argument.objects.bulk_update(
            bulk_update,
            fields=[
                "detailed_content",
            ],
        )
        legal_memo = Legal_Memorandum.objects.get(id=request.data.get("legal_memo"))

        # send mail (detailed legal_memo)
        send_legal_memo_detail(legal_memo)

        legal_memo.case_history.is_completed = True
        legal_memo.case_history.save()

        return HttpResponseRedirect(
            reverse(
                "brief_argument:admin_home_page",
            )
        )


class AIBExammViewsets(viewsets.ModelViewSet):
    queryset = AIB_EXAM.objects.all()
    serializer_class = AIBExamSerializer

    def create(self, request, *args, **kwargs):
        aib_exam_obj = self.queryset.filter(
            question=request.data.get("question"),
            option_a=request.data.get("option_a"),
            option_b=request.data.get("option_b"),
            option_c=request.data.get("option_c"),
            option_d=request.data.get("option_d"),
            is_completed=False,
        ).exists()
        if aib_exam_obj:
            return Response(
                {"Error": "This Question with Options is aldready present!!"},
                status=status.HTTP_404_NOT_FOUND,
            )
        else:
            data = {
                "question": request.data.get("question"),
                "option_a": request.data.get("option_a"),
                "option_b": request.data.get("option_b"),
                "option_c": request.data.get("option_c"),
                "option_d": request.data.get("option_d"),
            }
            serializer = self.get_serializer(data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return HttpResponseRedirect(
                reverse(
                    "brief_argument:aib_exam",
                )
            )

    def update(self, request, *args, **kwargs):
        aib_exam_obj = self.get_object()
        if request.data.get("step_2") == True:
            send_aib_mail(request.data.get("aib_final_result"))
            aib_exam_obj.is_completed = True
            aib_exam_obj.save()
            print("It is working::")
            return HttpResponseRedirect(
                reverse(
                    "brief_argument:aib_exam_admin_page",
                )
            )
        aib_relevant_topic_content = relevent_topics_input_generator(
            request.data.get("aib_relevant_topics"), aib=True
        )
        if aib_exam_obj is None:
            return Response(
                {"error": "BriefArgument not found"}, status=status.HTTP_404_NOT_FOUND
            )
        data = {
            "relevant_topics_content": aib_relevant_topic_content,
        }
        serializer = self.get_serializer(aib_exam_obj, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        self.get_success_headers(serializer.data)
        return HttpResponseRedirect(
            reverse(
                "brief_argument:aib_step_2",
                kwargs={"aib_exam_id": aib_exam_obj.id},
            )
        )


class LegalMemorandumViewsets(viewsets.ModelViewSet):
    queryset = Legal_Memorandum.objects.all()
    serializer_class = LegalMemorandumSerializer

    def create(self, request, *args, **kwargs):
        input_relevant_topic = relevent_topics_input_generator(
            request.data.get("research_output"), aib=False
        )
        data = {
            "relevant_topics": input_relevant_topic,
        }
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        legal_memo = serializer.save()
        case_history = CaseHistory.objects.get(id=request.data.get("case_id"))
        case_history.legal_memo = legal_memo
        case_history.save()
        self.get_success_headers(serializer.data)
        return HttpResponseRedirect(
            reverse(
                "brief_argument:step_2",
                kwargs={"legal_memo_id": serializer.data["id"]},
            )
        )

    def update(self, request, *args, **kwargs):
        (
            full_legal_memo_original,
            full_legal_memo_html,
            legal,
            facts,
            analysis,
            conclusion,
        ) = step_2_output_formatter(request.data.get("counsel_output"))
        legal_memo_obj = self.get_object()
        if legal_memo_obj is None:
            return Response(
                {"error": "BriefArgument not found"}, status=status.HTTP_404_NOT_FOUND
            )
        data = {
            "legal": legal,
            "facts": facts,
            "full_legal_memo_original": full_legal_memo_original,
            "full_legal_memo_html": full_legal_memo_html,
            "conclusion": conclusion,
        }
        serializer = self.get_serializer(legal_memo_obj, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        for anal in analysis:
            anal.update({"legal_memo": legal_memo_obj.id})
        Argument.objects.filter(legal_memo=legal_memo_obj).delete()
        argument_serializer = ArgumentSerializer(data=analysis, many=True, partial=True)
        argument_serializer.is_valid(raise_exception=True)
        argument_serializer.save()
        self.get_success_headers(serializer.data)
        return HttpResponseRedirect(
            reverse(
                "brief_argument:step_3",
                kwargs={"legal_memo_id": serializer.data["id"]},
            )
        )


class HulsburyLawBooksViewsets(viewsets.ModelViewSet):
    queryset = HulsburyLawBooks.objects.all()
    serializer_class = HulsburyLawBooksSerializer


class StatementEmbeddingsViewsets(viewsets.ModelViewSet):
    queryset = StatementEmbeddings.objects.all()
    serializer_class = StatementEmbeddingsSerializer

    @action(detail=False, methods=["POST"])
    def search(self, request, pk=None):
        search_text = request.data.get("search_text")
        print("search text::", search_text)

        embedding = openai.embeddings.create(
            input=[search_text], model="text-embedding-3-large"
        )
        search_history = LegalSearchHistory.objects.filter(
            search_text=request.data.get("search_text"),
            embeddings=embedding.data[0].embedding,
        )
        if not search_history.exists():
            search_history = LegalSearchHistory.objects.create(
                search_text=request.data.get("search_text"),
                embeddings=embedding.data[0].embedding,
            )

        statement_result = StatementEmbeddings.objects.order_by(
            CosineDistance("embeddings", embedding.data[0].embedding)
        ).values_list("husbury_file")

        # final_result = (
        #     RelevantCitationsPassage.objects.filter(
        #         husbury_file__id__in=statement_result
        #     )
        #     .order_by(CosineDistance("embeddings", embedding.data[0].embedding))
        #     .values("doc_name", "passage")
        # )[:10]
        final_result = (
            RelevantCitationsPassage.objects.filter(
                husbury_file__id__in=statement_result
            )
            .annotate(
                score_value=CosineDistance("embeddings", embedding.data[0].embedding)
            )
            .order_by("score_value")
            .values("score_value", "doc_name", "passage")
        )

        return Response({"result": final_result}, status=status.HTTP_201_CREATED)


class RelevantCitationsPassageViewsets(viewsets.ModelViewSet):
    queryset = RelevantCitationsPassage.objects.all()
    serializer_class = RelevantCitationsPassageSerializer


def main_page(request):
    # case_notes = CaseNote.objects.all()
    # index = 0
    # case_notes_ids = []
    # for case_note in case_notes:
    #     pattern = r"\(Para[^)]*\)"
    #     case_note.short_text = case_note.short_text.replace("\n", '')
    #     case_note.short_text = case_note.short_text.replace("\t", '')
    #     case_note.short_text = re.sub(pattern, "", case_note.short_text)
    #     case_note.short_text = case_note.short_text
    #     case_notes_ids.append(case_note)
    #     index += 1
    #     print("Case Notes::", index)
    # print(":::::::Case Notes BUlk Update::::::")
    # CaseNote.objects.bulk_update(case_notes_ids, ['short_text'])
    # print("::::::: Case Notes Done::::::")
    ### Removing the number from paragraph text and adding the number in the apra_count
    # case_notes = Caseparagraph.objects.all()
    # id_list = []
    # index = 0
    # for case in case_notes:
    #     print(case.id)
    #     match = re.search(r'^\s*(\d+(?:\.\d+)?)', case.text)
    #     try:
    #         case.para_count = match.group(0)
    #         case.text = case.text.replace(f"{match.group(0)}.",'')
    #         id_list.append(case)
    #         case.save()
    #         print("not working")
    #         print('not working TEXT::', case.text)
    #         print("not working PARA:::", case.para_count)
    #         print()
    # print("Bulk Updating")
    # print("::::::: Case Paragraphs BUlk Update ::::::")
    # # Caseparagraph.objects.bulk_update(id_list, ['text', 'para_count'])
    # print("::::::: Case Paragraph Done::::::")
    # step2_setup()
    # print("EMPTY CASE PARA:::",Case.objects.filter(paragraph__isnull=True).count())
    # get_top_cases("This is the text of task 1", "This is the query text")
    # print(CaseNote.objects.filter(case__id='4def5390-17ed-4f91-a456-a0c62a857c4e').values_list("short_text", flat=True))
    # case_notes = (
    #     CaseNote.objects.all()
    #     .values("id", "short_text")[:3]
    # )
    # dict_value = {index: case["id"] for index, case in enumerate(case_notes)}

    # print("CASES::", [doc for doc in case_notes])
    print(perplexity_scrape_selenium("https://www.perplexity.ai/page/session-of-the-flat-An8Ly5R5Tj.IsN3A.ZWxAA"))
    csrf_token = get_token(request)
    return render(request, "brief_argument/main_page.html", {"csrf_token": csrf_token})


def step_1(request, case_id):
    csrf_token = get_token(request)
    case_history = CaseHistory.objects.get(id=case_id)
    system_instruction = get_step_1_input_part2(
        case_history.legal_issue,
        case_history.fact_case,
    )
    context = {
        "research_input": system_instruction,
        "csrf_token": csrf_token,
    }
    return render(request, "brief_argument/step_1.html", context)


def step_2(request, legal_memo_id):
    legal_memo = Legal_Memorandum.objects.get(id=legal_memo_id)
    sof = legal_memo.sof
    legal_issue = legal_memo.case_history.legal_issue
    sof = sof.replace("<p>", "")
    sof = sof.replace("</p>", "")
    sof = sof.replace("<br>", "")
    sof = sof.replace("Statement of Facts", "")
    openai.api_key = os.getenv("OPEN_AI")
    sof_embeddings = openai.embeddings.create(
        input=[f"{legal_issue}{sof}{legal_issue}"], model="text-embedding-3-large"
    )
    case_notes = (
        CaseNote.objects.annotate(
            case_note_score=CosineDistance(
                "embeddings", sof_embeddings.data[0].embedding
            )
        )
        .order_by("case_note_score")[:50]
        .prefetch_related(
            Prefetch(
                "paragraph",
                queryset=Caseparagraph.objects.annotate(
                    para_score=CosineDistance(
                        "embeddings", sof_embeddings.data[0].embedding
                    ),
                ),
                to_attr="paragraph_value",
            ),
        )
    )
    csrf_token = get_token(request)

    system_instruction = get_step_2_input_part2(
        facts=legal_memo.case_history.fact_case,
        legal_issue=legal_memo.case_history.legal_issue,
        sof=sof,
        case=get_case_notes_and_ratio_para(case_notes),
    )
    # print("SYStem ::", system_instruction)
    context = {
        "csrf_token": csrf_token,
        "input_1": system_instruction,
    }
    return render(request, "brief_argument/step_2.html", context)


def step_3(request, legal_memo_id):
    # optimize the query using Prefetch
    legal_memo = (
        Legal_Memorandum.objects.filter(id=legal_memo_id)
        .prefetch_related("analysis", "case_history")
        .first()
    )
    facts = legal_memo.case_history.fact_case
    legal = legal_memo.case_history.legal_issue
    sof = legal_memo.sof
    brief_answer = legal_memo.brief_answer
    intro = legal_memo.decision_intro
    total_input = []
    all_discussion = ""
    for anal in legal_memo.analysis.all():
        all_discussion += f"<{anal.title}>{anal.content}</{anal.title}>"
    for anal in legal_memo.analysis.all():
        total_input.append(
            {
                "ids": anal.id,
                "input": step_3_input_part2(
                    facts,
                    legal,
                    anal.title,
                    intro,
                    anal.content,
                    sof,
                    legal_memo.question,
                    brief_answer,
                    all_discussion,
                    decision_value(anal.title, anal.content, sof),
                ),
            }
        )
    step_3_input_json = json.dumps(total_input)
    csrf_token = get_token(request)
    context = {
        "csrf_token": csrf_token,
        "step_3_input": total_input,
        "step_3_length": len(total_input),
        "step_3_input_json": step_3_input_json,
    }
    return render(request, "brief_argument/step_3.html", context)


def step_4(request, legal_memo_id):
    legal_memo = (
        Legal_Memorandum.objects.filter(id=legal_memo_id)
        .prefetch_related("analysis", "case_history")
        .first()
    )
    facts = legal_memo.case_history.fact_case
    legal_issue = legal_memo.case_history.legal_issue
    sof = legal_memo.sof
    sof = sof.replace("<p>", "")
    sof = sof.replace("</p>", "")
    sof = sof.replace("<br>", "")
    sof = sof.replace("Statement of Facts", "")
    brief_answer = legal_memo.brief_answer
    brief_answer.replace("<p>", "")
    brief_answer.replace("</p>", "")
    brief_answer.replace("<br>", "")
    question = legal_memo.question
    question = question.replace("<p>", "")
    question = question.replace("</p>", "")
    decision_intro = legal_memo.decision_intro
    decision_intro = decision_intro.replace("<p>", "")
    decision_intro = decision_intro.replace("</p>", "")
    decision_text = ""
    for anal in legal_memo.analysis.all():
        content = anal.detailed_content
        content = content.replace("<p>", "")
        content = content.replace("</p>", "")
        content = content.replace("<br>", "")
        title = anal.title
        title = title.replace("<p>", "")
        title = title.replace("</p>", "")
        title = title.replace("<br>", "")
        decision_text += f"""<{title}> {content} </{title}> """
    step_4_input = get_step_4_input_part2(
        facts, legal_issue, question, sof, brief_answer, decision_intro, decision_text
    )
    csrf_token = get_token(request)
    context = {
        "csrf_token": csrf_token,
        "step_4_input": step_4_input,
    }
    return render(request, "brief_argument/step_4.html", context)


def step_5(request, legal_memo_id):
    legal_memo = (
        Legal_Memorandum.objects.filter(id=legal_memo_id)
        .prefetch_related("analysis", "case_history")
        .first()
    )
    sof = legal_memo.sof
    sof = sof.replace("<p>", "")
    sof = sof.replace("</p>", "")
    sof = sof.replace("<br>", "")
    sof = sof.replace("Statement of Facts", "")
    brief_answer = legal_memo.brief_answer
    brief_answer = brief_answer.replace("<p>", "")
    brief_answer = brief_answer.replace("</p>", "")
    brief_answer = brief_answer.replace("<br>", "")
    question = legal_memo.question
    question = question.replace("<p>", "")
    question = question.replace("</p>", "")
    decision_intro = legal_memo.decision_intro
    decision_intro = decision_intro.replace("<p>", "")
    decision_intro = decision_intro.replace("</p>", "")
    decision_conclusion = legal_memo.decision_conclusion
    decision_conclusion = decision_conclusion.replace("<p>", "")
    decision_conclusion = decision_conclusion.replace("</p>", "")
    conclusion = legal_memo.conclusion
    conclusion = conclusion.replace("<p>", "")
    conclusion = conclusion.replace("</p>", "")
    decision_text = ""
    index = 1
    for anal in legal_memo.analysis.all():
        content = anal.detailed_content
        content = content.replace("<p>", "")
        content = content.replace("</p>", "")
        content = content.replace("<br>", "")
        title = anal.title
        title = title.replace("<p>", "")
        title = title.replace("</p>", "")
        title = title.replace("<br>", "")
        decision_text += f"""<{title}> {content} </{title}> """
        # decision_text += f"""<subsection_{index}><{title}> {content} </{title}></subsection_{index}>"""
        index += 1
    step_5_input = get_step_5_input_part2(
        question, sof, brief_answer, decision_text, conclusion
    )
    csrf_token = get_token(request)
    context = {
        "csrf_token": csrf_token,
        "step_5_input": step_5_input,
    }
    return render(request, "brief_argument/step_5.html", context)


def admin_home_page(request):
    case_history = CaseHistory.objects.filter(is_completed=False).order_by(
        "created_date"
    )
    count = case_history.count()
    case_history_obj = case_history.first()
    context = {
        "case_history": case_history_obj,
        "count": count,
        "Values": "HAHHAAH",
    }
    return render(request, "brief_argument/admin_home_page.html", context)


def aib_exam(request):
    csrf_token = get_token(request)
    context = {
        "csrf_token": csrf_token,
    }
    return render(request, "brief_argument/aib_exam.html", context)


def aib_step_1(request, aib_exam_id):
    aib_exam = AIB_EXAM.objects.get(id=aib_exam_id)
    input = aib_exam__step_1_input(
        aib_exam.question,
        aib_exam.option_a,
        aib_exam.option_b,
        aib_exam.option_c,
        aib_exam.option_d,
    )
    csrf_token = get_token(request)
    context = {
        "csrf_token": csrf_token,
        "aib_input": input,
    }
    return render(request, "brief_argument/aib_step_1.html", context)


def aib_step_2(request, aib_exam_id):
    aib_exam = AIB_EXAM.objects.get(id=aib_exam_id)
    input = aib_exam_step_2_input(
        aib_exam.relevant_topics_content,
        aib_exam.question,
        aib_exam.option_a,
        aib_exam.option_b,
        aib_exam.option_c,
        aib_exam.option_d,
    )
    csrf_token = get_token(request)
    context = {
        "csrf_token": csrf_token,
        "aib_input": input,
    }
    return render(request, "brief_argument/aib_step_2.html", context)


def aib_exam_adim_page(request):
    aib_exam = AIB_EXAM.objects.filter(is_completed=False).order_by("created_date")
    count = aib_exam.count()
    aib_exam_obj = aib_exam.first()
    context = {
        "aib_exam": aib_exam_obj,
        "count": count,
    }
    return render(request, "brief_argument/aib_exam_admin.html", context)


def legal_memo_frontend(request, legal_memo_id):
    legal_memo = (
        Legal_Memorandum.objects.filter(id=legal_memo_id)
        .prefetch_related("analysis", "case_history")
        .first()
    )
    legal = legal_memo.legal
    facts = legal_memo.facts
    title = legal_memo.case_history.legal_issue
    analysis = []
    for anal in legal_memo.analysis.all():
        analysis.append(
            {
                "title": anal.title,
                "content": anal.content,
            }
        )
    conclusion = legal_memo.conclusion
    legal = legal.replace("'", "\\'")
    facts = facts.replace("'", "\\'")
    conclusion = conclusion.replace("'", "\\'")
    context = {
        "title": mark_safe(title),
        "legal": mark_safe(legal),
        "facts": mark_safe(facts),
        "detailed_analyis": json.dumps(analysis),
        "conclusion": mark_safe(conclusion),
    }
    return render(request, "brief_argument/legal_memo_fe.html", context)


def legal_search(request):
    csrf_token = get_token(request)
    context = {
        "csrf_token": csrf_token,
    }
    return render(request, "brief_argument/legal_search_2.html", context)


def cocounsel_worker_1(request):
    csrf_token = get_token(request)
    context = {
        "csrf_token": csrf_token,
    }
    return render(request, "brief_argument/cc_worker_1.html", context)

def cocounsel_worker_2(request, cc_case_id):
    csrf_token = get_token(request)
    context = {
        "csrf_token": csrf_token,
    }
    return render(request, "brief_argument/cc_worker_2.html", context)
