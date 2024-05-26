import re
from legal_gpt import settings
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render
from rest_framework.response import Response
from django.core.mail import EmailMultiAlternatives
from django.core.cache import cache
from django.template.loader import render_to_string
from rest_framework import viewsets
from .models import Argument, BriefArgument
from rest_framework import status
from case_history.models import CaseHistory
from case_history.models import LawTopics
from .serializers import ArgumentSerializer, BriefArgumentSerializer
from django.middleware.csrf import get_token


INPUT_TOPICS = """<Law 1>Constitutional Law<Topic 1.1>FUNDAMENTAL RIGHTS: MEANING OF STATE AND LAW (Articles 12-13)<Token>29406</Token></Topic 1.1><Topic 1.2>RIGHT TO EQUALITY (Articles 14-18)<Token>49262</Token></Topic 1.2><Topic 1.3>Right to Freedom (Articles 19-22)<Token>54975</Token></Topic 1.3><Topic 1.4>RIGHT AGAINST EXPLOITATION (Articles 23-24)<Token>1515</Token></Topic 1.4><Topic 1.5>RIGHT TO FREEDOM OF RELIGION (Articles 25-28)<Token>9622</Token></Topic 1.5><Topic 1.6>CULTURAL AND EDUCATIONAL RIGHTS (Articles 29-30)<Token>10760</Token></Topic 1.6><Topic 1.7>RIGHT TO CONSTITUTIONAL REMEDIES (Article 32)<Token>7717</Token></Topic 1.7><Topic 1.8>FUNDAMENTAL DUTIES (Article 51A)<Token>1980</Token></Topic 1.8><Topic 1.9>DIRECTIVE PRINCIPLES OF STATE POLICY (Articles 36-51)<Token>4557</Token></Topic 1.9><Topic 1.10>THE AMENDMENT OF THE CONSTITUTION (Article 368)<Token>21918</Token></Topic 1.10></Law 1>"""


def get_sys_instruct_research(petitioner_name, respondent_name):
    return f"""this is the Research System INstruction of {petitioner_name} and {respondent_name}."""


def get_instruct_research(petitioner_name, respondent_name):
    return f"""this is just theResearch  Instruction of {petitioner_name} and {respondent_name}."""


def get_sys_instruct_counsel(petitioner_name, respondent_name):
    return f"""this is the Counsel System Instruction of {petitioner_name} and {respondent_name}."""


def get_instruct_counsel(petitioner_name, respondent_name):
    return f"""this is the Counsel Instruction of {petitioner_name} and {respondent_name}."""


class ArgumentViewSet(viewsets.ModelViewSet):
    queryset = Argument.objects.all()
    serializer_class = ArgumentSerializer


class BriefArgumentViewSet(viewsets.ModelViewSet):
    queryset = BriefArgument.objects.all()
    serializer_class = BriefArgumentSerializer

    def create(self, request, *args, **kwargs):
        research_output = request.data.get("research_output")
        cache.set("research_output", research_output, timeout=None)
        input_relevant_topic = self.relevent_topics_input_generator(research_output)
        brief_argument_data = {
            "relevant_topics": input_relevant_topic,
        }
        serializer = self.get_serializer(data=brief_argument_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        self.perform_create(serializer)
        case_history = CaseHistory.objects.get(id=request.data.get("case_id"))
        case_history.brief_argument_id = serializer.data["id"]
        case_history.save()
        self.get_success_headers(serializer.data)
        return HttpResponseRedirect(
            reverse(
                "brief_argument:counsel_input",
                kwargs={"brief_id": serializer.data["id"]},
            )
        )

    def update(self, request, *args, **kwargs):
        (
            argument_list,
            introduction,
            argument_title,
            draft_argument,
            prayer,
            conclusion,
            legal_principles,
            factual_analysis,
        ) = self.counsel_formatter(request.data.get("counsel_output"))
        brief_argument_obj = self.get_object()
        if brief_argument_obj is None:
            return Response(
                {"error": "BriefArgument not found"}, status=status.HTTP_404_NOT_FOUND
            )
        data = {
            "legal_principal": legal_principles,
            "factual_analysis": factual_analysis,
            "draft_argument": draft_argument,
            "conclusion": conclusion,
            "prayer": prayer,
            "title": argument_title,
            "introduction": introduction,
            "case_name": f"{brief_argument_obj.case_history.petitioner_name}v.{brief_argument_obj.case_history.respondent_name} in {brief_argument_obj.case_history.high_court}",
        }
        serializer = self.get_serializer(brief_argument_obj, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        argument_serializer = ArgumentSerializer(data=argument_list, many=True)
        argument_serializer.is_valid(raise_exception=True)
        argument_objects = argument_serializer.save()
        brief_argument_obj.argument_value.clear()
        brief_argument_obj.argument_value.add(*argument_objects)
        brief_argument_obj.save()
        # if cache.get("research_output") is None:
        #     pass
        # else:
        #     print("Working::")
        self.send_brief_email(brief_argument_obj.id, cache.get("research_output"))
        return HttpResponseRedirect(
            reverse(
                "brief_argument:admin_home_page",
            )
        )

    def counsel_formatter(self, string):
        legal_principles = re.findall(
            r"<legal_principles>(.*?)</legal_principles>", string, re.DOTALL
        )
        factual_analysis = re.findall(
            r"<factual_analysis>(.*?)</factual_analysis>", string, re.DOTALL
        )
        argument_title = re.findall(
            r"<argument_title>(.*?)</argument_title>", string, re.DOTALL
        )
        prayer = re.findall(r"<prayer>(.*?)</prayer>", string, re.DOTALL)
        conclusion = re.findall(r"<conclusion>(.*?)</conclusion>", string, re.DOTALL)
        introduction = re.findall(
            r"<introduction>(.*?)</introduction>", string, re.DOTALL
        )
        arguments = re.findall(
            r"<arg(\d+)_detailed>(.*?)</arg\d+_detailed>", string, re.DOTALL
        )
        arguments_title = re.findall(r"<arg_(\d+)>(.*?)</arg_\d+>", string, re.DOTALL)
        argument_list = []
        draft_argument = []
        for arg in arguments:
            for arg_title in arguments_title:
                arg_number, arg_text = arg
                arg_title_number, arg_title = arg_title
                if arg_number == arg_title_number:
                    arg_text = arg_text.replace("\n\n", "<br><br>")
                    arg_text = arg_text.replace("'", "&apos;")
                    arg_text = arg_text.replace("\n", "<br>")
                    arg_dict = {
                        "content": arg_text,
                        "title": arg_title,
                    }
                    draft_argument.append(arg_title)
                    argument_list.append(arg_dict)
        new_prayer = []
        for p in prayer:
            new_p = p.replace("\n\n", "<br><br>")
            new_p = p.replace("'", "&apos;")
            new_p = p.replace("\n", "<br>")
            new_prayer.append(new_p)

        legal_principles = "\n".join(legal_principles)
        factual_analysis = "\n".join(factual_analysis)
        conclusion = "\n".join(conclusion)
        prayer = "\n".join(new_prayer)
        argument_title = "\n".join(argument_title)
        introduction = "\n".join(introduction)
        draft_argument = "\n".join(draft_argument)
        return (
            argument_list,
            introduction,
            argument_title,
            draft_argument,
            prayer,
            conclusion,
            legal_principles,
            factual_analysis,
        )

    def relevent_topics_input_generator(self, topics):
        topics = LawTopics.objects.filter(name__in=topics)
        topics_input_value = ""
        for i, topic in enumerate(topics, start=1):
            topics_input_value += f"<Topic {i}>{topic.content}<Token>{topic.token_value}</Token></Topic {i}>"
        return topics_input_value

    def send_brief_email(self, brief_id, _relevant_topics):
        brief_argument_obj = BriefArgument.objects.get(id=brief_id)
        relevent_topics = LawTopics.objects.filter(name__in=_relevant_topics)
        html_content = render_to_string(
            "email/brief_argument.html",
            context={
                "brief_argument": brief_argument_obj,
                "relevent_topics": relevent_topics,
            },
        )
        subject = f"{brief_argument_obj.case_history.petitioner_name} v. {brief_argument_obj.case_history.respondent_name} in {brief_argument_obj.case_history.high_court}"
        from_email = settings.EMAIL_HOST_USER
        recipient_list = ["mithileshtheledgend@gmail.com"]
        message = EmailMultiAlternatives(
            subject, body="", from_email=from_email, to=recipient_list
        )
        message.attach_alternative(html_content, "text/html")
        message.send()
        brief_argument_obj.case_history.is_completed = True
        brief_argument_obj.case_history.save()


def main_page(request):
    csrf_token = get_token(request)
    return render(request, "brief_argument/main_page.html", {"csrf_token": csrf_token})


def research_input(request, case_id):
    csrf_token = get_token(request)
    case_history = CaseHistory.objects.get(id=case_id)
    system_instruction = get_sys_instruct_research(
        case_history.petitioner_name, case_history.respondent_name
    )
    instruction =  get_instruct_research(
        case_history.petitioner_name, case_history.respondent_name
    )
    legal_fact = f"<Fact of the case>{case_history.fact_case}</Fact of the case><Legal Issue>{case_history.legal_issue}</Legal Issue>"
    input_topics = INPUT_TOPICS
    research_input = f"{system_instruction}{input_topics}{legal_fact}{instruction}"
    # print("REFSAD::", research_input)
    context = {
        # "system_instruction": get_sys_instruct_research(
        #     case_history.petitioner_name, case_history.respondent_name
        # ),
        # "instruction": get_instruct_research(
        #     case_history.petitioner_name, case_history.respondent_name
        # ),
        # "legal_fact": f"<Fact of the case>{case_history.fact_case}</Fact of the case><Legal Issue>{case_history.legal_issue}</Legal Issue>",
        # "input_topics": INPUT_TOPICS,
        "research_input": research_input,
        "csrf_token": csrf_token,
    }
    return render(request, "brief_argument/reseach_input.html", context)


# def law_topics_format_generator():
#     parent_objs = LawTopics.objects.filter(parent__isnull=True)
#     input_law_topics = ""
#     for i, parent_obj in enumerate(parent_objs, start=1):
#         input_law_topics += f"<Law {i}>{parent_obj.name}"
#         for y, child_obj in enumerate(parent_obj.lawtopics_set.all(), start=1):
#             input_law_topics += f"<Topic {i}.{y}>{child_obj.name}<Token>{child_obj.token_value}</Token></Topic {i}.{y}>"
#         input_law_topics += f"</Law {i}>"
#     return input_law_topics


def counsel_input(request, brief_id):
    brief_argument = BriefArgument.objects.get(id=brief_id)
    csrf_token = get_token(request)
    system_instruction = get_sys_instruct_counsel(
            brief_argument.case_history.petitioner_name,
            brief_argument.case_history.respondent_name,
        )
    legal_value = brief_argument.case_history.legal_issue
    fact_value = brief_argument.case_history.fact_case
    law_topics = brief_argument.relevant_topics
    input_1 = f"{system_instruction}{law_topics}{fact_value}{legal_value}"
    context = {
        "csrf_token": csrf_token,
        # "system_instruction": get_sys_instruct_counsel(
        #     brief_argument.case_history.petitioner_name,
        #     brief_argument.case_history.respondent_name,
        # ),
        # "law_topics": brief_argument.relevant_topics,
        # "fact_value": brief_argument.case_history.fact_case,
        # "legal_value": brief_argument.case_history.legal_issue,
        "input_1": input_1,
        "instruction": get_instruct_counsel(
            brief_argument.case_history.petitioner_name,
            brief_argument.case_history.respondent_name,
        ),
    }
    return render(request, "brief_argument/counsel_input.html", context)


def admin_home_page(request):
    case_history = (
        CaseHistory.objects.filter(is_completed=False).order_by("created_date")
    )
    count = case_history.count()
    case_history_obj = case_history.first()
    context = {
        "case_history": case_history_obj,
        "count": count,
    }
    return render(request, "brief_argument/admin_home_page.html", context)
