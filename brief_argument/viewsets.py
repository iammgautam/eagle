from collections import defaultdict
import openai
import os
import re
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db.models import Prefetch, Q, Count
from django.db.models.functions import Coalesce
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
    CoCounsel,
)
from brief_argument.models import default_embeddings
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
    CaseSerializerValue,
    CoCounselSerializers,
)
from .utils import (
    final_cocounsel,
    get_research_and_query,
    get_sof_and_question,
    get_step4_output_formatter,
    get_top_cases,
    legal_memo_formatter,
    perplexity_scrape,
    send_legal_memo_detail,
    relevent_topics_input_generator,
    send_aib_mail,
    step_2_output_formatter,
    step_2_output_formatter_part2,
    get_selected_parapgraphs,
    get_all_case_paragraphs,
)


class ArgumentViewSet(viewsets.ModelViewSet):
    queryset = Argument.objects.all()
    serializer_class = ArgumentSerializer

    def create(self, request, *args, **kwargs):
        bulk_update = []
        for analysis in request.data.get("detailed_analysis"):
            print("TEXT:::", analysis["detailed_content"])
            match = (
                re.search(
                    "&lt;&lt;.*?&gt;&gt;((?:(?!&lt;&lt;).)*?)&lt;&lt;/.*?&gt;&gt;",
                    analysis["detailed_content"],
                )
                .group(1)
                .strip()
            )
            print("VALUESS:::", match)
            bulk_update.append(Argument(id=analysis["id"], detailed_content=match))
        Argument.objects.bulk_update(
            bulk_update,
            fields=[
                "detailed_content",
            ],
        )
        return HttpResponseRedirect(
            reverse(
                "brief_argument:step_4",
                kwargs={"legal_memo_id": request.data.get("legal_memo")},
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
        sof = get_sof_and_question(request.data.get("step_1_op"))
        data = {
            "sof": sof,
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
            research_analysis_text,
            question_text,
            decision,
            intro_text,
            conclusio_text,
            brief_anwser,
        ) = step_2_output_formatter_part2(request.data.get("counsel_output"))
        legal_memo_obj = self.get_object()
        if legal_memo_obj is None:
            return Response(
                {"error": "BriefArgument not found"}, status=status.HTTP_404_NOT_FOUND
            )
        data = {
            "question": question_text,
            "decision_intro": intro_text,
            "decision_conclusion": conclusio_text,
            "brief_answer": brief_anwser,
        }
        serializer = self.get_serializer(legal_memo_obj, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        for anal in decision:
            anal.update({"legal_memo": legal_memo_obj.id})
        Argument.objects.filter(legal_memo=legal_memo_obj).delete()
        argument_serializer = ArgumentSerializer(data=decision, many=True, partial=True)
        argument_serializer.is_valid(raise_exception=True)
        argument_serializer.save()
        self.get_success_headers(serializer.data)
        return HttpResponseRedirect(
            reverse(
                "brief_argument:step_3",
                kwargs={"legal_memo_id": serializer.data["id"]},
            )
        )

    @action(detail=True, methods=["PUT"])
    def step4(self, request, pk=None):
        legal_memo_obj = self.get_object()
        print("LEGAL::", legal_memo_obj)
        if legal_memo_obj is None:
            return Response(
                {"error": "BriefArgument not found"}, status=status.HTTP_404_NOT_FOUND
            )
        conclusion = get_step4_output_formatter(request.data.get("conclusion_data"))
        data = {
            "conclusion": conclusion,
        }
        serializer = self.get_serializer(legal_memo_obj, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return HttpResponseRedirect(
            reverse(
                "brief_argument:step_5",
                kwargs={"legal_memo_id": serializer.data["id"]},
            )
        )

    @action(detail=True, methods=["PUT"])
    def step5(self, request, pk=None):
        legal_memo_obj = self.get_object()
        if legal_memo_obj is None:
            return Response(
                {"error": "BriefArgument not found"}, status=status.HTTP_404_NOT_FOUND
            )
        brief_answer, sof, conclusion, decision_value, full_legal_memo_original = (
            legal_memo_formatter(request.data.get("memo_data"))
        )
        data = {
            "full_legal_memo_html": full_legal_memo_original,
            "brief_answer": brief_answer,
            "sof": sof,
            "conclusion": conclusion,
        }
        serializer = self.get_serializer(legal_memo_obj, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        decision = Argument.objects.filter(legal_memo=legal_memo_obj)
        # print("DECISION;::", decision)
        for decision_val in decision_value:
            for anal in decision:
                print("ANAL TITLE::", anal)
                print("DECISION::", decision_val["title"])
                if anal.title == decision_val["title"]:
                    anal.final_legal_text = decision_val["content"]
                    anal.save()

        # send mail (detailed legal_memo)
        send_legal_memo_detail(legal_memo_obj)

        legal_memo_obj.case_history.is_completed = True
        legal_memo_obj.case_history.save()
        return HttpResponseRedirect(
            reverse(
                "brief_argument:admin_home_page",
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
    def case_text(self, request):
        case_ids = request.data.get("case_ids")
        queryset = self.get_queryset()
        result = queryset.filter(id__in=case_ids).prefetch_related(
            Prefetch(
                "paragraph",
                queryset=Caseparagraph.objects.all(),
                to_attr="para_text",
            )
        )
        serializer = CaseSerializerValue(result, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["POST"])
    def lexplore_search(self, request):
        openai.api_key = os.getenv("OPEN_AI")
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
            .order_by("case_note_score")[:20]
            .prefetch_related(
                Prefetch(
                    "paragraph",
                    queryset=Caseparagraph.objects.annotate(
                        para_score=CosineDistance(
                            "embeddings", search_text_embeddings.data[0].embedding
                        ),
                    ),
                    to_attr="paragraph_value",
                ),
                Prefetch(
                    "case",
                    queryset=Case.objects.all().prefetch_related(
                        "paragraph",
                        Prefetch(
                            "case_note",
                            queryset=CaseNote.objects.prefetch_related("paragraph"),
                            to_attr="case_notes_query",
                        ),
                    ),
                    to_attr="case_query",
                ),
            )
        )
        result = []
        para_score_list = []
        index = 0
        for case_note in case_notes:
            for para in case_note.paragraph_value:
                para_score_list.append(para.para_score)
                index += 1
        case_note_average_score = min(para_score_list)
        for case_note in case_notes:
            selected_paragraphs = self.get_selected_parapgraphs(
                case_note.case_query, case_note.embeddings
            )
            case_paragraphs = get_all_case_paragraphs(case_note.case_query)
            para_list = []
            selected_para_ids = set()
            para_list = [
                {
                    "id": para.id,
                    "number": int(para.number),
                    "para_score": (
                        1 if para.selected_para_score < case_note_average_score else 0
                    ),
                }
                for para in selected_paragraphs
            ]
            selected_para_ids.update(para.id for para in selected_paragraphs)
            para_list.extend(
                {
                    "id": para.id,
                    "number": int(para.number),
                    "para_score": 0,
                }
                for para in case_paragraphs
                if para.id not in selected_para_ids
            )
            para_list.sort(key=lambda x: x["number"])
            for para in para_list:
                del para["number"]

            result.append(
                {
                    "case_id": case_note.case.id,
                    "case_note_score": case_note.case_note_score,
                    "paragraphs": para_list,
                }
            )
        result = sorted(
            [
                {**item, "case_note_average_score": min(para_score_list)}
                for item in result
            ],
            key=lambda x: x["case_note_score"],
            reverse=False,
        )
        for para in result:
            del para["case_note_score"]
            del para["case_note_average_score"]

        return Response({"result": result}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["POST"])
    def case_search(self, request):
        openai.api_key = os.getenv("OPEN_AI")
        search_text = request.data.get("search_text")
        text_embedding = openai.embeddings.create(
            input=[search_text], model="text-embedding-3-large"
        )

        case_notes = (
            CaseNote.objects.annotate(
                case_note_score=CosineDistance(
                    "embeddings", text_embedding.data[0].embedding
                )
            )
            .order_by("case_note_score")[:23]
            .prefetch_related(
                Prefetch(
                    "case",
                    queryset=Case.objects.all().prefetch_related(
                        Prefetch(
                            "case_references",
                            queryset=Case.objects.all(),
                            to_attr="case_references_query",
                        ),
                        Prefetch(
                            "referring_cases",
                            queryset=Case.objects.all(),
                            to_attr="referring_cases_query",
                        ),
                    ),
                    to_attr="case_query",
                ),
            )
        )

        threshold_score = case_notes[22].case_note_score
        # print("Threshold ::", threshold_score)
        text_case_note_value = ""
        alpha_cases = set()
        for case_note in case_notes:
            text_case_note_value += f"{search_text}{case_note}"
            original_case = case_note.case_query
            # get the case id of the current case_note
            alpha_cases.add(original_case.id)
            alpha_cases.update(ref.id for ref in original_case.case_references_query)
            alpha_cases.update(ref.id for ref in original_case.referring_cases_query)
        # print("ALpha Cases::", alpha_cases)
        # case_count = Case.objects.filter(id__in=list(alpha_cases)).annotate(
        #     case_count_value=Count("case_note")
        # )
        # for case in case_count:
        #     print(f"Case id::{case.id} ---- CaseCount Value {case.case_count_value}")
        text_case_note_value += f"{search_text}"

        text_embedding = openai.embeddings.create(
            input=[text_case_note_value], model="text-embedding-3-large"
        )
        case_scores = {case: 0 for case in alpha_cases}
        selected_para_ids = {case: [] for case in alpha_cases}
        paragraph = (
            Caseparagraph.objects.filter(
                Q(case__in=list(alpha_cases)), ~Q(embeddings=default_embeddings)
            )
            .annotate(
                para_score=CosineDistance(
                    "embeddings", text_embedding.data[0].embedding
                )
            )
            .order_by("para_score")
        )
        for para in paragraph:
            case_id = para.case.id
            # print('Case Idd::', case_id)
            selected_para_ids[case_id].append(para.id)
            if case_scores[case_id] < 500:
                case_scores[case_id] += para.text.count(" ")
            if len([score for score in case_scores.values() if score > 98]) >= 23:
                break

        beta_cases = sorted(case_scores.items(), key=lambda x: x[1], reverse=True)[:23]
        # print("Beta cases::", beta_cases)
        # print("Selected para::", selected_para_ids)
        # for i, v in selected_para_ids.items():
        #     print(f"selected para list::{i}---{v}")
        #     print()
        result = []
        for case_id, _ in beta_cases:
            highlighted_para = []
            # print("HMMM::", selected_para_ids[case_id])
            # print()
            for para_id in selected_para_ids[case_id]:
                para = paragraph.get(id=para_id)
                if para.para_score < threshold_score:
                    # print("Para Score::::", para.para_score)
                    highlighted_para.append(para_id)
            result.append({"case_id": case_id, "highlighted_para": highlighted_para})

        return Response({"result": result}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["POST"])
    def case_search_1(self, request):
        openai.api_key = os.getenv("OPEN_AI")
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
            .order_by("case_note_score")[:20]
            .prefetch_related(
                Prefetch(
                    "paragraph",
                    queryset=Caseparagraph.objects.annotate(
                        para_score=CosineDistance(
                            "embeddings", search_text_embeddings.data[0].embedding
                        ),
                    ),
                    to_attr="paragraph_value",
                ),
                Prefetch(
                    "case",
                    queryset=Case.objects.all().prefetch_related(
                        "paragraph",
                        Prefetch(
                            "case_note",
                            queryset=CaseNote.objects.prefetch_related("paragraph"),
                            to_attr="case_notes_query",
                        ),
                    ),
                    to_attr="case_query",
                ),
            )
        )
        result = []
        para_score_list = []
        index = 0
        for case_note in case_notes:
            for para in case_note.paragraph_value:
                para_score_list.append(para.para_score)
                index += 1
        case_note_average_score = min(para_score_list)
        for case_note in case_notes:
            selected_paragraphs = self.get_selected_parapgraphs(
                case_note.case_query, case_note.embeddings
            )
            case_paragraphs = self.get_all_case_paragraphs(case_note.case_query)
            para_list = []
            selected_para_ids = set()
            para_list = [
                {
                    "id": para.id,
                    "text": para.text,
                    "number": int(para.number),
                    "para_score": (
                        1 if para.selected_para_score < case_note_average_score else 0
                    ),
                }
                for para in selected_paragraphs
            ]
            selected_para_ids.update(para.id for para in selected_paragraphs)
            para_list.extend(
                {
                    "id": para.id,
                    "text": para.text,
                    "number": int(para.number),
                    "para_score": 0,
                }
                for para in case_paragraphs
                if para.id not in selected_para_ids
            )
            para_list.sort(key=lambda x: x["number"])
            for para in para_list:
                del para["number"]

            result.append(
                {
                    "case_id": case_note.case.id,
                    "petitioner": case_note.case.petitioner,
                    "respondent": case_note.case.respondent,
                    "court": case_note.case.court,
                    "judges": case_note.case.judges,
                    "case_note_score": case_note.case_note_score,
                    "paragraphs": para_list,
                }
            )
        result = sorted(
            [
                {**item, "case_note_average_score": min(para_score_list)}
                for item in result
            ],
            key=lambda x: x["case_note_score"],
            reverse=False,
        )
        for para in result:
            del para["case_note_score"]
            del para["case_note_average_score"]

        return Response({"result": result}, status=status.HTTP_200_OK)

    def get_selected_parapgraphs(self, case, query_embedding):
        case_note_para = set()
        citation_paragraphs = set()
        for case_note in case.case_notes_query:
            for para in case_note.paragraph.all():
                case_note_para.add(para.para_count)
        for item in case.citations:
            if item["paragraph"] is not None:
                citation_paragraphs.update(item["paragraph"])
        combined_set = list(case_note_para.union(citation_paragraphs))
        return (
            Caseparagraph.objects.filter(
                para_count__in=combined_set,
                case=case,
            )
            .annotate(selected_para_score=CosineDistance("embeddings", query_embedding))
            .order_by("selected_para_score")
        )

    def get_all_case_paragraphs(self, case):
        return case.paragraph.all()


class CoCounselViewSets(viewsets.ModelViewSet):
    queryset = CoCounsel.objects.all()
    serializer_class = CoCounselSerializers

    def create(self, request):
        data = {
            "legal_issue": request.data.get("legal_issue"),
            "brief_facts": request.data.get("brief_facts"),
            "case_facts": request.data.get("case_facts"),
            "legal_research": request.data.get("legal_research"),
        }
        serializer = self.get_serializer(data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["GET"])
    def get_cc_case(self, request):
        try:
            cc_case = (
                self.get_queryset().filter(is_completed=False).latest("created_date")
            )
            input_1 = f"{cc_case.brief_facts} {cc_case.legal_issue}"
            input_2 = f"{cc_case.case_facts}"
            input_3 = f"{cc_case.legal_research}"
            cc_case_id = f"{cc_case.id}"
            return Response(
                {
                    "input_1": input_1,
                    "input_2": input_2,
                    "input_3": input_3,
                    "cc_case_id": cc_case_id,
                },
                status=status.HTTP_200_OK,
            )
        except CoCounsel.DoesNotExist:
            return Response(
                {
                    "result": "All task complete. Please wait and reload after sometime for new task"
                },
                status=status.HTTP_404_NOT_FOUND,
            )

    @action(detail=False, methods=["GET"])
    def get_cocounse_value(self, request):
        try:
            cc_case = (
                self.get_queryset().filter(is_completed=False).earliest("created_date")
            )
            serializer = self.get_serializer(cc_case)
            return Response(
                serializer.data,
                status=status.HTTP_200_OK,
            )
        except CoCounsel.DoesNotExist:
            return Response(
                {
                    "result": "All task complete. Please wait and reload after sometime for new task"
                },
                status=status.HTTP_404_NOT_FOUND,
            )

    @action(detail=True, methods=["PUT"])
    def step_1(self, request, pk=None):
        cc_case_obj = self.get_object()
        if cc_case_obj is None:
            return Response(
                {"error": "CoCounsel not found"}, status=status.HTTP_404_NOT_FOUND
            )
        research_analysis, search_query = get_research_and_query(
            request.data.get("step_1_op")
        )
        data = {
            "research_analysis": research_analysis,
            "search_query": search_query,
        }
        serializer = self.get_serializer(cc_case_obj, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return HttpResponseRedirect(
            reverse(
                "brief_argument:cc_worker_2",
                kwargs={"cc_case_id": serializer.data["id"]},
            )
        )

    @action(detail=True, methods=["PUT"])
    def get_case_ids(self, request, pk=None):
        cc_case_obj = self.get_object()
        top_cases = final_cocounsel(request.data.get("step_1_op"))
        # print("Top caases::", top_cases)
        cases_data = Case.objects.filter(id__in=top_cases)
        cases_serialized_data = CaseSerializer(cases_data, many=True).data
        data = {
            "research_analysis": request.data.get("step_1_op"),
            "case_ids_list": f"{cases_serialized_data}",
        }
        serializer = self.get_serializer(cc_case_obj, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # Convert the UUIDs to strings (if they're not already) and append .txt
        case_id_strings = [f"{str(uuid)}.txt" for uuid in top_cases]
        # Format the string
        formatted_case_ids = " ".join(f'"{uuid}"' for uuid in case_id_strings)
        # print(formatted_case_ids)
        return Response(formatted_case_ids, status=status.HTTP_200_OK)

    @action(detail=True, methods=["GET"])
    def get_step_2(self, request, pk=None):
        cc_case_obj = self.get_object()
        input_1 = f"{cc_case_obj.search_query}"
        top_cases = get_top_cases(
            cc_case_obj.research_analysis, cc_case_obj.search_query
        )
        render_case = []
        for case in top_cases:
            render_case.append(
                {
                    "id": case["case__id"],
                    "code": case["case__code"],
                }
            )
        print("RENDERSER::", render_case)
        case_ids = [str(item["case__id"]) for item in top_cases]
        data = {
            "case_ids_list": f"{render_case}",
        }
        serializer = self.get_serializer(cc_case_obj, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        input_list = self.get_selected_para(case_ids)
        return Response(
            {
                "input_1": input_1,
                "case_para_list": input_list,
                "case_ids_list": case_ids,
                "case_id": cc_case_obj.id,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["POST"])
    def step_2_submit(self, request, pk=None):
        cc_case_obj = self.get_object()
        # cocounsel_data = perplexity_scrape(request.data.get("link"))
        print("LINK", request.data.get("link"))
        data = {
            "is_completed": True,
            "scrape_link": request.data.get("link"),
        }
        serializer = self.get_serializer(cc_case_obj, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return HttpResponseRedirect(reverse("brief_argument:cc_worker_1"))

    def get_selected_para(self, case_ids):
        cases = Case.objects.filter(id__in=case_ids).prefetch_related(
            Prefetch(
                "case_note",
                queryset=CaseNote.objects.all().prefetch_related(
                    Prefetch(
                        "paragraph",
                        queryset=Caseparagraph.objects.all(),
                        to_attr="case_note_para_query",
                    ),
                ),
                to_attr="case_note_query",
            )
        )
        input_list = []
        for index, case in enumerate(cases, start=2):
            case_note_para = set()
            citation_paragraphs = set()
            for case_note in case.case_note_query:
                for para in case_note.case_note_para_query:
                    case_note_para.add(para.para_count)
            for item in case.citations:
                if item["paragraph"] is not None:
                    citation_paragraphs.update(item["paragraph"])
            combined_set = list(case_note_para.union(citation_paragraphs))
            paragraphs = (
                Caseparagraph.objects.filter(case=case, para_count__in=combined_set)
                .order_by("para_count")
                .values_list("text", flat=True)
            )
            paragraph_text = ".".join(paragraphs)
            input_list.append({f"input_{index}": paragraph_text})

        return input_list
    
def count_referring_cases(case_ids):
    referring_case_counts = defaultdict(int)

    # Fetch the referring cases for the given IDs
    cases = Case.objects.filter(id__in=case_ids).prefetch_related(
        Prefetch(
            "referring_cases",
            queryset=Case.objects.all(),
            to_attr="referring_cases_query",
        )
    )

    for case in cases:
        referring_case_counts[case.id] += len(case.referring_cases_query.all())

    return referring_case_counts


# Assuming you have the necessary imports and models defined
def get_case_references(case_ids, seen_ids=None, case_counts=None):
    if seen_ids is None:
        seen_ids = set()
    if case_counts is None:
        case_counts = defaultdict(int)

    # Fetch the cases for the given IDs
    cases = Case.objects.filter(id__in=case_ids).prefetch_related(
        Prefetch(
            "case_references",
            queryset=Case.objects.all(),
            to_attr="case_references_query",
        )
    )

    # Collect the IDs of the case references
    new_case_ids = []
    for case in cases:
        if case.id not in seen_ids:
            seen_ids.add(case.id)
            case_counts[case.id] += 1
            for ref_case in case.case_references_query.all():
                if ref_case.id not in seen_ids:
                    new_case_ids.append(ref_case.id)

    # Recursively fetch the case references for the new IDs
    if new_case_ids:
        return get_case_references(new_case_ids, seen_ids, case_counts)

    return seen_ids, case_counts


def final_function(text):
    openai.api_key = os.getenv("OPEN_AI")
    text_embedding = openai.embeddings.create(
        input=[text], model="text-embedding-3-large"
    )

    case_notes = (
        CaseNote.objects.annotate(
            case_note_score=CosineDistance(
                "embeddings", text_embedding.data[0].embedding
            )
        )
        .order_by("case_note_score")[:4]
        .prefetch_related(
            Prefetch(
                "case",
                queryset=Case.objects.all().prefetch_related(
                    Prefetch(
                        "case_references",
                        queryset=Case.objects.all(),
                        to_attr="case_references_query",
                    ),
                    Prefetch(
                        "referring_cases",
                        queryset=Case.objects.all(),
                        to_attr="referring_cases_query",
                    ),
                ),
                to_attr="case_query",
            ),
        )
    ).values("case__id","case_note_score")

    # Extract case IDs and case note scores from the case notes
    case_ids = [note['case__id'] for note in case_notes]
    case_notes_score = {note['case__id']: note['case_note_score'] for note in case_notes}

    # Get all case references recursively and keep track of counts
    all_case_ids_set, case_counts = get_case_references(case_ids)

    # Convert the set to a list of UUIDs
    all_case_ids = list(all_case_ids_set)

    # Get the counts of referring cases for all collected case IDs
    referring_case_counts = count_referring_cases(all_case_ids)

    # Calculate the product of case_counts, referring_case_counts, and case_note_score
    case_scores = {}
    for case_id in all_case_ids:
        case_scores[case_id] = (
            case_counts[case_id] *
            referring_case_counts[case_id] *
            case_notes_score.get(case_id, 0)  # Default to 0 if case_id not in case_notes_score
        )

    # Sort the case scores from highest to lowest
    sorted_case_scores = sorted(case_scores.items(), key=lambda item: item[1], reverse=True)

    # Get the top 4 case IDs with the highest scores
    top_4_case_ids = [case_id for case_id, score in sorted_case_scores[:4]]

    # Print or use the collected case IDs and their counts
    print("All Case IDs:", all_case_ids)
    print("Case Counts:", case_counts)