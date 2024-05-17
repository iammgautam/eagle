import asyncio, re
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets
from .models import Argument, BriefArgument
from rest_framework import status
from case_history.models import CaseHistory
from case_history.models import LawTopics
from .serializers import ArgumentSerializer, BriefArgumentSerializer
from .main import brief_researcher, brief_counsel


class ArgumentViewSet(viewsets.ModelViewSet):
    queryset = Argument.objects.all()
    serializer_class = ArgumentSerializer


class BriefArgumentViewSet(viewsets.ModelViewSet):
    queryset = BriefArgument.objects.all()
    serializer_class = BriefArgumentSerializer

    @action(methods=["POST"], detail=False)
    def create_or_update_brief_argument(self, request):
        case_history = request.data.get("case_history")
        case_history = CaseHistory.objects.get(id=case_history)
        facts_legal = f"<Fact of the case>{case_history.fact_case}</Fact of the case><Legal Issue>{case_history.legal_issue}</legal Issue>"
        fact_value = f"<Fact of the case>{case_history.fact_case}</Fact of the case>"
        legal_value = f"<Legal Issue>{case_history.legal_issue}</legal Issue>"
        SYS_INST = "Rithik will give me"
        INST = "Chotu will give me"
        input_topics_format = self.law_topics_format_generator()
        relevant_law_topics = asyncio.run(
            brief_researcher(SYS_INST, INST, facts_legal, input_topics_format)
        )
        relevant_law_topics = '''
            Here are the relevant law topics that need to be researched to address whether the Right to Life of the people of Valabhpur is being violated under Article 21 of the Constitution:
            <Relevant_Topics>
            <Topic 1.3>Right to Freedom (Articles 19-22)</Topic 1.3>
            <Topic 1.7>RIGHT TO CONSTITUTIONAL REMEDIES (Article 32)</Topic 1.7>
            </Relevant_Topics>
        '''
        pattern = r"<Topic[^>]*>([^<]*)"
        matches = re.findall(pattern, relevant_law_topics)
        relevent_topics_list = []
        for match in matches:
            relevent_topics_list.append(match)
        print("INPUTS::::", relevent_topics_list)
        input_relevant_topic = self.relevent_topics_input_generator(
            relevent_topics_list
        )
        print("WHAT IS THE INPUT::", input_relevant_topic)
        brief_argument_output = asyncio.run(
            brief_counsel(SYS_INST, INST, fact_value, legal_value, input_relevant_topic)
        )
        print("BRIEF_ARGUMENT:::", brief_argument_output)
        print("RELEVENT_TOPICS::", relevant_law_topics)

        return Response({"Result": brief_argument_output}, status=status.HTTP_200_OK)

    def law_topics_format_generator(self):
        parent_objs = LawTopics.objects.filter(parent__isnull=True)
        input_law_topics = ""
        for i, parent_obj in enumerate(parent_objs, start=1):
            input_law_topics += f"<Law {i}>{parent_obj.name}"
            for y, child_obj in enumerate(parent_obj.lawtopics_set.all(), start=1):
                input_law_topics += f"<Topic {i}.{y}>{child_obj.name}<Token>{child_obj.token_value}</Token></Topic {i}.{y}>"
            input_law_topics += f"</Law {i}>"
        return input_law_topics

    def relevent_topics_input_generator(self, topics):
        topics = LawTopics.objects.filter(name__in=topics)
        topics_input_value = ""
        for i, topic in enumerate(topics, start=1):
            topics_input_value += f"<Topic {i}{topic.content}<Token>{topic.token_value}</Token></Topic {i}>"
        return topics_input_value
