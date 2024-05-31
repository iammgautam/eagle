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


def get_step_1_input(topics, facts, legal_issue):
    return f"""You are a legal researcher tasked with finding the most relevant and applicable law topics for a particular legal case. To assist you, I will provide three key pieces of information:

            <allLawTopics>
            {topics}
            </allLawTopics>

            <facts>
            {facts}
            </facts>

            <legalIssue>
            {legal_issue}
            </legalIssue>

            Please follow these steps carefully:

            1. Read the facts of the case and the legal issue thoroughly to fully understand the details and context of the case.

            2. Review the provided list of law topics, paying close attention to how they are segmented and described. Make sure you have a clear grasp of what each topic entails.

            3. Select the law topics that are most relevant and applicable to the case at hand, based on your analysis of the facts and the legal issue that needs to be addressed.

            4. Check the cumulative size of your selected law topics. If the total size exceeds 125000, carefully deselect the least relevant and applicable topics from your list until the cumulative size is reduced to 125000 or below.

            5. Provide your final curated list of the most relevant and applicable law topics for this case inside <relevant&applicableLawTopics> tags, formatted as follows:

            <relevant&applicableLawTopics>
            [list the relevant and applicable law topics here]
            </relevant&applicableLawTopics>

            Remember, your goal is to identify the law topics that are most pertinent and useful for addressing the legal issue, given the specific facts of the case. Carefully consider the relevance and applicability of each topic before making your final selections.

            Sample Response Format:
            <relevant&applicableLawTopics>
            Topic 1.2: Topic_1.2_name <size>topic_1.2_size</size>
            Topic 1.9: Topic_1.9_name <size>topic_1.9_size</size>
            Topic 1.10: Topic_1.10_name <size>topic_1.10_size</size>
            Total size: topic_1.2_size + topic_1.9_size + topic_1.10_size
            </relevant&applicableLawTopics>
            """


def get_step_2_input(relevent_topics, fact, legal_issue):
    return f"""
        You are a legal researcher tasked with drafting a legal memorandum for a particular case. To complete this task, please follow these steps: 

        1. Carefully read and understand the statement of law provided: 

        <statement_of_law> 
        {relevent_topics} 
        </statement_of_law> 

        2. Study the facts of the case: 

        <facts_of_the_case> 
        {fact} 
        </facts_of_the_case> 

        3. Consider the legal question to be addressed: 

        <legal_question> 
        {legal_issue} 
        </legal_question> 

        4. Before proceeding, take time to thoroughly understand the statement of law, facts of the case, and the legal question. 

        5. Structure your legal memorandum as follows: 

        a. Question Presented 
        - Formulate a specific and impartial question that captures the core legal issue without assuming a legal conclusion. 

        b. Statement of Facts 
        - Provide a concise, impartial summary of the key facts relevant to the legal matter, approximately 200 words in length. 
        - Include current and past legal proceedings related to the issue. 
        - Present the facts chronologically or grouped thematically, whichever format offers the clearest understanding. 

        c. Analysis 
        - Provide a well-reasoned legal analysis, discussing the application of the law to the facts of the case, incorporating the relevant legal principles (statutes and case laws) from the statement of law and facts from the case.
        - outline the various legal topics to be addressed and provide an analysis of the legal issue, usually ordered in subsections. 
        - Divide the analysis into subsections, each addressing a specific legal topic relevant to the case in atleast 500 words in length. 
        - For each topic, clearly state the applicable law and relevant facts in an active voice and present your analysis in a logical manner. 
        - The total length of the Analysis section should be approximately 2000 words. 

        d. Conclusion 
        - In approximately 300 words, predict how the court will likely apply the law based on your analysis. 
        - Express your level of confidence in the prediction based on the available information. 
        - Using an impartial advisory tone, identify next steps and propose a legal strategy to proceed. 

        6. Provide your complete legal memorandum inside <legal_memorandum> tags. 

        Remember to provide a thorough and well-reasoned legal analysis, incorporating the relevant legal principles from the statement of law, facts of the case, and application of law to the facts. Your memorandum should demonstrate a clear understanding of the legal issues at hand and provide valuable insights for the reader.

    """


class ArgumentViewSet(viewsets.ModelViewSet):
    queryset = Argument.objects.all()
    serializer_class = ArgumentSerializer


class BriefArgumentViewSet(viewsets.ModelViewSet):
    queryset = BriefArgument.objects.all()
    serializer_class = BriefArgumentSerializer

    def create(self, request, *args, **kwargs):
        research_output = request.data.get("research_output")
        input_relevant_topic = self.relevent_topics_input_generator(research_output)
        brief_argument_data = {
            "relevant_topics": input_relevant_topic,
        }
        serializer = self.get_serializer(data=brief_argument_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        case_history = CaseHistory.objects.get(id=request.data.get("case_id"))
        case_history.brief_argument_id = serializer.data["id"]
        case_history.save()
        self.get_success_headers(serializer.data)
        return HttpResponseRedirect(
            reverse(
                "brief_argument:step_2",
                kwargs={"brief_id": serializer.data["id"]},
            )
        )

    def update(self, request, *args, **kwargs):
        string = self.counsel_formatter(request.data.get("counsel_output"))
        html_content = render_to_string(
            "email/example.html",
            context={
                "string": string,
            },
        )
        brief_argument_obj = self.get_object()
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
        return HttpResponseRedirect(
            reverse(
                "brief_argument:admin_home_page",
            )
        )

    def counsel_formatter(self, string):

        string = string.replace(
            "a. Question Presented", "<h2><b>Question Presented</b></h2>"
        )
        string = string.replace(
            "b. Statement of Facts", "<h2><b>Statement of Facts</b></h2>"
        )
        string = string.replace("c. Analysis", "<h2><b>Analysis</b></h2>")
        string = string.replace("d. Conclusion", "<h2><b>Conclusion</b></h2>")
        string = re.search(
            r"&lt;legal_memorandum&gt;(.*?)&lt;\/legal_memorandum&gt;",
            string,
            re.DOTALL,
        ).group(1)
        return string

    def relevent_topics_input_generator(self, topics):
        topics = LawTopics.objects.filter(name__in=topics)
        topics_input_value = ""
        for topic in topics:
            topics_input_value += f"{topic.content}"
        return topics_input_value

    # def send_brief_email(self, brief_id, _relevant_topics):
    #     brief_argument_obj = BriefArgument.objects.get(id=brief_id)
    #     relevent_topics = LawTopics.objects.filter(name__in=_relevant_topics)
    #     html_content = render_to_string(
    #         "email/brief_argument.html",
    #         context={
    #             "brief_argument": brief_argument_obj,
    #             "relevent_topics": relevent_topics,
    #         },
    #     )
    #     subject = f"{brief_argument_obj.case_history.petitioner_name} v. {brief_argument_obj.case_history.respondent_name} in {brief_argument_obj.case_history.high_court}"
    #     from_email = settings.EMAIL_HOST_USER
    #     recipient_list = ["mithileshtheledgend@gmail.com"]
    #     message = EmailMultiAlternatives(
    #         subject, body="", from_email=from_email, to=recipient_list
    #     )
    #     message.attach_alternative(html_content, "text/html")
    #     message.send()
    #     brief_argument_obj.case_history.is_completed = True
    #     brief_argument_obj.case_history.save()


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
    return render(request, "brief_argument/reseach_input.html", context)


# def law_topics_format_generator():
#     parent_objs = LawTopics.objects.filter(parent__isnull=True)
#     input_law_topics = ""
#     for i, parent_obj in enumerate(parent_objs, start=1):
#         input_law_topics += f"<Law {i}>{parent_obj.name}"
#         for y, child_obj in enumerate(parent_obj.lawtopics_set.all(), start=1):
#             input_law_topics += f"<Topic {i}.{y}>{child_obj.name}<size>{child_obj.token_value}</size></Topic {i}.{y}>"
#         input_law_topics += f"</Law {i}>"
#     return input_law_topics


def step_2(request, brief_id):
    brief_argument = BriefArgument.objects.get(id=brief_id)
    csrf_token = get_token(request)
    system_instruction = get_step_2_input(
        brief_argument.relevant_topics,
        brief_argument.case_history.fact_case,
        brief_argument.case_history.legal_issue,
    )
    context = {
        "csrf_token": csrf_token,
        "input_1": system_instruction,
    }
    return render(request, "brief_argument/counsel_input.html", context)


def admin_home_page(request):
    # law_topics_format_generator()
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
