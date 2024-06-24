import openai
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db.models import Prefetch, Avg
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from pgvector.django import CosineDistance

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
    LegalResearchStep1Serializer,
    StatementEmbeddingsSerializer,
    RelevantCitationsPassageSerializer,
    CaseNoteSerializer,
    CaseSerializer,
    CaseparagraphSerializer,
)
from .utils import (
    send_legal_memo_detail,
    relevent_topics_input_generator,
    send_aib_mail,
    step_2_output_formatter,
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


class CaseViewsets(viewsets.ModelViewSet):
    queryset = Case.objects.all()
    serializer_class = CaseparagraphSerializer

    @action(detail=False, methods=["POST"])
    def step_1_search(self, request):
        search_text = request.data.get("search_text")
        search_text_embeddings = openai.embeddings.create(
            input=[search_text], model="text-embedding-3-large"
        )
        case_notes = (
            CaseNote.objects.annotate(
                case_note_score=CosineDistance(
                    "embeddings", search_text_embeddings.data[0].embedding
                )
            )
            .order_by("case_note_score")[:10]
            .prefetch_related(
                Prefetch(
                    "paragraph",
                    queryset=Caseparagraph.objects.annotate(
                        para_score=CosineDistance(
                            "embeddings", search_text_embeddings.data[0].embedding
                        ),
                    ),
                    to_attr="paragraph_value",
                )
            )
        )
        result = []
        for case_note in case_notes:
            para_score_sum = 0
            index = 0
            para_list = []
            for para in case_note.paragraph_value:
                para_list.append(
                    {
                        "id": para.id,
                        "text": para.text,
                        "para_score": para.para_score,
                    }
                )
                para_score_sum += para.para_score
                index += 1
            ratio_score = para_score_sum / index
            result.append(
                {
                    "id": case_note.id,
                    "case_note": case_note.short_text,
                    "case": case_note.case.code,
                    "respondent_name": case_note.case.petitioner,
                    "petitioner_name": case_note.case.respondent,
                    "court": case_note.case.court,
                    "ratio_score": ratio_score,
                    "paragraph_value": para_list,
                }
            )
        result = sorted(result, key=lambda x: x["ratio_score"], reverse=True)

        return Response({"result": result}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'])
    def step_1_search_2(self, request):
        search_text = request.data.get("search_text")
        search_text_embeddings = openai.embeddings.create(
            input=[search_text], model="text-embedding-3-large"
        )
