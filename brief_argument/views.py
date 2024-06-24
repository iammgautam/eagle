import re
import json
import openai
import numpy as np
from django.db import transaction
from django.db.models import Func, Value, FloatField, Count, Max, TextField
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
    Legal_Memorandum,
    AIB_EXAM,
    HulsburyLawBooks,
    StatementEmbeddings,
    RelevantCitationsPassage,
    Case,
    CaseNote,
    Caseparagraph,
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
    INPUT_TOPICS,
    get_step_1_input,
    get_step_2_input_with_lr,
    get_step_2_input_without_lr,
    get_step_3_input_with_lr,
    get_step_3_input_without_lr,
    import_air,
    open_ai_keyword_api,
    read_word_doc,
    send_legal_memo_detail,
    aib_exam__step_1_input,
    aib_exam_step_2_input,
    relevent_topics_input_generator,
    send_aib_mail,
    step_2_output_formatter,
    law_topics_format_generator,
    update_the_citation,
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
    # import_air()
    # case = Case.objects.values('code').annotate(count=Count('code')).filter(count__gt=1)
    # case_code = []
    # for i in case:
    #     case_code.append(i['code'])
    # case = Case.objects.filter(code__in=case_code).distinct('code')
    # # print(case)
    # for i in case:
    #     print(f"{i}--{i.code}")
    #     print()
    #     i.delete
    ###Long text remove para
    # First, define the list of zeros
    # caseparagraphs = Caseparagraph.objects.filter(embeddings=np.zeros(3072))
    # print(caseparagraphs)
    # case = Case.onjects.all()
    # for case in case:
    #     for para in case.citations:
    #         print(para)
    #     print()
    # index = 1
    # for case_note in case_notes:
    #     pattern = r"\(Para[^)]*\)"
    #     case_note.short_text = case_note.short_text.replace("\n", '')
    #     case_note.short_text = case_note.short_text.replace("\t", '')
    #     case_note.short_text = re.sub(pattern, "", case_note.short_text)
    #     case_note.save()
    #     index += 1
    ### Removing the number from paragraph text and adding the number in the apra_count
    # case_notes = Caseparagraph.objects.all()
    # id_list = []
    # for case in case_notes:
    #     print(case.id)
    #     match = re.search(r'^\s*(\d+(?:\.\d+)?)', case.text)
    #     try:
    #         case.para_count = match.group(0)
    #         case.text = case.text.replace(f"{match.group(0)}.",'')
    #         # print('TEXT::', text_value)
    #         # print("PARA:: COunt::", case.para_count)
    #         print()
    #         case.save()
    #         id_list.append(case.id)
    #     except:
    #         print("not working")
    #         print('not working TEXT::', case.text)
    #         print("not working PARA:::", case.para_count)
    #         print()
    # print("Final List::", id_list)
    # case_notes_with_keywords = []
    # for case_note in case_notes:
    #     keywords = open_ai_keyword_api(case_note.short_text)
    #     case_note.keywords = keywords
    #     case_notes_with_keywords.append(case_note)

    # with transaction.atomic():
    #     for case_note in case_notes_with_keywords:
    #         case_note.save()

    csrf_token = get_token(request)
    return render(request, "brief_argument/main_page.html", {"csrf_token": csrf_token})


def step_1(request, case_id):
    csrf_token = get_token(request)
    case_history = CaseHistory.objects.get(id=case_id)
    system_instruction = get_step_1_input(
        INPUT_TOPICS, case_history.fact_case, case_history.legal_issue
    )
    context = {
        "research_input": system_instruction,
        "csrf_token": csrf_token,
    }
    return render(request, "brief_argument/step_1.html", context)


def step_2(request, legal_memo_id):
    legal_memo = Legal_Memorandum.objects.get(id=legal_memo_id)
    csrf_token = get_token(request)
    if legal_memo.case_history.legal_research:
        system_instruction = get_step_2_input_with_lr(
            relevent_topics=legal_memo.relevant_topics,
            facts=legal_memo.case_history.fact_case,
            legal=legal_memo.case_history.legal_issue,
            research=legal_memo.case_history.legal_research,
        )
    else:
        system_instruction = get_step_2_input_without_lr(
            relevent_topics=legal_memo.relevant_topics,
            facts=legal_memo.case_history.fact_case,
            legal=legal_memo.case_history.legal_issue,
        )
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
    relevent_topics = legal_memo.relevant_topics
    legal_memo_original = legal_memo.full_legal_memo_original
    total_input = []
    is_legal_research_present = bool(legal_memo.case_history.legal_research)
    for anal in legal_memo.analysis.all():
        if is_legal_research_present:
            total_input.append(
                {
                    "ids": anal.id,
                    "input": get_step_3_input_with_lr(
                        legal_memo_original,
                        relevent_topics,
                        facts,
                        legal,
                        anal.title,
                        anal.content,
                        legal_memo.case_history.legal_research,
                    ),
                }
            )
        else:
            total_input.append(
                {
                    "ids": anal.id,
                    "input": get_step_3_input_without_lr(
                        legal_memo_original,
                        relevent_topics,
                        facts,
                        legal,
                        anal.title,
                        anal.content,
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


def admin_home_page(request):
    working = update_the_citation()
    # filtered_content = read_word_doc(
    #     "v:line",
    #     "/Users/mithilesh/law/Animals/fwdanimals",
    # )
    # print("WHAT IS THIS::", working)
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
    # open_ai_keyword_api(
    #     "(D) Special Marriage Act (43 of 1954) , S.4— Solemnisation of marriage - For same-sex couples - By reading down of statutory provisions - Provision of SMA cannot be read as 'gender neutral' provision - Right to marry cannot be read into provisions of SMA, so as to include same sex marriages - SMA to include marriages between heterosexual relationships only. DOCTRINE - Doctrine of 'reading down' - Applicability.In the instant case, the petitioners sought permission for same-sex couples to solemnise their marriages under the Special Marriage Act, by applying doctrine of reading down to statutory provisions. Held, provision of Special Marriage Act (SMA) cannot be read as 'gender neutral' provision. Right to marry cannot be read into provisions of SMA, so as to include same sex marriages. SMA to include marriages between heterosexual relationships only. (Per Dr. Dhananjaya Chandrachud, C.J.I.) - The judicial legislation is impermissible. Reading words into the provisions of the SMA and provisions of other allied laws would essentially entail delving into the realm of the legislature. The Court is not equipped to undertake an exercise of such wide amplitude because of its institutional limitations. The court usually first determines if the law is unconstitutional, and then proceeds to decide on the relief. However, in this case, an exercise to determine whether the SMA is unconstitutional because of under-inclusivity would be futile because of the limitations of this Court's power to grant a remedy. Whether a change should be brought into the legislative regime of the SMA is for Parliament to determine. Parliament has access to varied sources of information and represents in itself a diversity of viewpoints in the polity. The Court in the exercise of the power of judicial review must be careful not to tread into the legislative domain.                (Sanjay Kishan Kaul, J. ) - Reading into the statute is beyond the powers of judicial review and would be under the legislative domain. It would also not be prudent to suspend or strike down the SMA, given that it is a beneficial legislation and is regularly and routinely used by heterosexual partners desirous of getting married. For this reason, this particular methodology of recognising the right of non-heterosexual partners to enter into a civil union, as opposed to striking down provisions of the SMA, ought to be considered as necessarily exceptional in nature. It should not restrict the Courts while assessing such deep-seated forms of discrimination in the future                (Per S. Ravindra Bhat, Hima Kohli, and Pamidighantam Sri Narasimha, JJ. ) - The provisions of SMA are incapable of being 'reading down', or interpreted by 'reading up' in the manner suggested by the petitioners. S. 4 of SMA (conditions relating to solemnization of special marriages), contemplates marriages between a man and a woman. To read SMA in any other manner would be contrary to established principles of statutory interpretation as discussed in preceding paragraphs. It is also not permissible for the court to 'read up' and substitute the words 'any two persons' to refer to a marriage between non-heterosexual couples. Furthermore, if provisions of SMA are to be construed as gender neutral (such as persons or spouses, in substitution of wife and husband) as the petitioners propose, it would be possible for a cis-woman's husband to file a case or create a narrative to manipulate the situation. Gender neutral interpretation of existing laws, therefore, would complicate an already exhausting path to justice for women and leave room for the perpetrator to victimise them. A law is not merely meant to look good on paper; but is an effective tool to remedy a perceived injustice, addressed after due evaluation about its necessity. A law which was consciously created and fought for, by women cannot, therefore, by an interpretive sleight be diluted."
    # )
    # keyword_list = []
    # case = CaseNote.objects.all()
    # index = 0
    # for cas in case:
    #     keyword = open_ai_keyword_api(cas)
    #     cas.keyword = keyword
    #     keyword_list.append(cas)
    #     index += 1
    #     print(index)
    # CaseNote.objects.bulk_update(keyword_list, ['keyword'])
    # print("keyword done::")
    # print()
    # print("Now Keyword Embeddings:")
    # keyword_list = []
    # index = 0
    # for case in case:
    #     embedding = openai.embeddings.create(
    #         input=[case.keyword], model="text-embedding-3-large"
    #     )
    #     cas.keyword_embeddings = embedding.data[0].embedding
    #     keyword_list.append(cas)
    #     index += 1
    #     print(index)
    # CaseNote.objects.bulk_update(keyword_list, ['keyword_embeddings'])
    csrf_token = get_token(request)
    context = {
        "csrf_token": csrf_token,
    }
    return render(request, "brief_argument/legal_search_2.html", context)
