import re
import json
from django.http import HttpResponseRedirect
from django.middleware.csrf import get_token
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response
from rest_framework import status
from django.urls import reverse
from django.shortcuts import render
from rest_framework import viewsets
from .models import Argument, Legal_Memorandum, AIB_EXAM
from case_history.models import CaseHistory
from .serializers import (
    ArgumentSerializer,
    LegalMemorandumSerializer,
    AIBExamSerializer,
)
from case_history.models import LawTopics
from .utils import (
    INPUT_TOPICS,
    get_step_1_input,
    get_step_2_input,
    get_step_3_input,
    send_legal_memo_basic,
    send_legal_memo_detail,
    aib_exam__step_1_input,
    aib_exam_step_2_input,
    relevent_topics_input_generator,
    send_aib_mail,
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

        # send mail (normal legal_memo)
        send_legal_memo_basic(legal_memo)
        # send mail (detailed legal_memo)
        send_legal_memo_detail(legal_memo)

        # legal_memo.case_history.is_completed = True
        # legal_memo.case_history.save()

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
            aib_exam_obj.is_completed=True
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
        ) = self.counsel_formatter(request.data.get("counsel_output"))
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

    def counsel_formatter(self, string):
        full_legal_memo_original = re.search(
            r"&lt;legal_memorandum&gt;(.*?)&lt;\/legal_memorandum&gt;",
            string,
            re.DOTALL,
        ).group(1)
        string = string.replace("<br>", "")
        if "!%!Question Presented!%!" in string or "Question Presented" in string:
            string = string.replace(
                "!%!Question Presented!%!", "<h2><b>Question Presented</b></h2>"
            ).replace("Question Presented", "<h2><b>Question Presented</b></h2>")

        if "!%!Statement of Facts!%!" in string or "Statement of Facts" in string:
            string = string.replace(
                "!%!Statement of Facts!%!", "<h2><b>Statement of Facts</b></h2>"
            ).replace("Statement of Facts", "<h2><b>Statement of Facts</b></h2>")

        if "!%!Analysis!%!" in string or "Analysis" in string:
            string = string.replace(
                "!%!Analysis!%!", "<h2><b>Analysis</b></h2>"
            ).replace("Analysis", "<h2><b>Analysis</b></h2>")

        if "!%!Conclusion!%!" in string or "Conclusion" in string:
            string = string.replace(
                "!%!Conclusion!%!", "<h2><b>Conclusion</b></h2>"
            ).replace("Conclusion", "<h2><b>Conclusion</b></h2>")
        full_legal_memo_html = re.search(
            r"&lt;legal_memorandum&gt;(.*?)&lt;\/legal_memorandum&gt;",
            string,
            re.DOTALL,
        ).group(1)
        pattern = r"\|\$\|(.*?)\|\$\|"
        matches = re.findall(pattern, full_legal_memo_html)
        for title in matches:
            full_legal_memo_html = full_legal_memo_html.replace(
                f"|$|{title}|$|", f"<b>{title}<b>"
            )
        # print("STRING:::", string)
        legal = re.search(
            r"Question Presented(.*?)Statement of Facts",
            string,
            re.DOTALL,
        ).group(1)

        facts = re.search(
            r"Statement of Facts(.*?)Analysis",
            string,
            re.DOTALL,
        ).group(1)

        analysis = re.search(
            r"Analysis(.*?)Conclusion",
            string,
            re.DOTALL,
        ).group(1)
        pattern = r"\|\$\|(.*?)\|\$\|"
        matches = re.findall(pattern, string)
        analysis = []
        for title in matches:
            pattern = rf"\|\$\|{title}\|\$\|(.*?)\|\$\|"
            if title == matches[-1]:
                pattern = rf"\|\$\|{title}\|\$\|(.*?)Conclusion"
            content_match = re.search(pattern, string, re.DOTALL).group(1)
            analysis.append({"title": title, "content": content_match})

        conclusion = re.search(
            r"Conclusion(.*?)&lt;\/legal_memorandum&gt;",
            string,
            re.DOTALL,
        ).group(1)

        return (
            full_legal_memo_original,
            full_legal_memo_html,
            legal,
            facts,
            analysis,
            conclusion,
        )

    def relevent_topics_input_generator(self, topics):
        pattern = r"\d+\.\d+:\s*(.*?)-\d+"
        matches = re.findall(pattern, topics)
        output = [match for match in matches]
        output = []
        for match in matches:
            if match.startswith('"') and match.endswith('"'):
                output.append(match.strip('"'))
            else:
                output.append(match)

        topics = LawTopics.objects.filter(name__in=output)
        topics_input_value = ""
        for topic in topics:
            topics_input_value += f"<{topic.name}>{topic.content}</{topic.name}>"
        return topics_input_value


def main_page(request):
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


def law_topics_format_generator():
    parent_objs = LawTopics.objects.filter(parent__isnull=True)
    input_law_topics = ""
    for i, parent_obj in enumerate(parent_objs, start=1):
        input_law_topics += f"Law {i} {parent_obj.name}:\n"
        for y, child_obj in enumerate(parent_obj.lawtopics_set.all(), start=1):
            input_law_topics += (
                f"Topic {i}.{y} {child_obj.name} Size:{child_obj.token_value},\n"
            )
    return input_law_topics


def step_2(request, legal_memo_id):
    legal_memo = Legal_Memorandum.objects.get(id=legal_memo_id)
    csrf_token = get_token(request)
    system_instruction = get_step_2_input(
        legal_memo.relevant_topics,
        legal_memo.case_history.fact_case,
        legal_memo.case_history.legal_issue,
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
        .prefetch_related("analysis")
        .first()
    )
    facts = legal_memo.case_history.fact_case
    legal = legal_memo.case_history.legal_issue
    relevent_topics = legal_memo.relevant_topics
    legal_memo_original = legal_memo.full_legal_memo_original
    total_input = []
    for anal in legal_memo.analysis.all():
        total_input.append(
            {
                "ids": anal.id,
                "input": get_step_3_input(
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
    case_history = CaseHistory.objects.filter(is_completed=False).order_by(
        "created_date"
    )
    count = case_history.count()
    case_history_obj = case_history.first()
    context = {
        "case_history": case_history_obj,
        "count": count,
    }
    return render(request, "brief_argument/admin_home_page.html", context)


def aib_exam(request):
    csrf_token = get_token(request)
    context = {
        "csrf_token": csrf_token,
    }
    return render(request, "brief_argument/aib_exam.html", context)


def aib_step_1(request, aib_exam_id):
    # print(law_topics_format_generator())
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
