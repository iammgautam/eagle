from rest_framework import serializers
from .models import (
    Argument,
    Legal_Memorandum,
    AIB_EXAM,
    HulsburyLawBooks,
    RelevantCitationsPassage,
    StatementEmbeddings,
    Case,
    CaseNote,
    Caseparagraph,
)


class ArgumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Argument
        fields = [
            "id",
            "title",
            "content",
            "detailed_content",
            "legal_memo",
            "created_date",
        ]


class AIBExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIB_EXAM
        fields = [
            "question",
            "option_a",
            "option_b",
            "option_c",
            "option_d",
            "answer",
            "relevant_topics_content",
            "is_completed",
        ]


class LegalMemorandumSerializer(serializers.ModelSerializer):
    # analysis_value = ArgumentSerializer(read_only=True, many=True)

    class Meta:
        model = Legal_Memorandum
        fields = [
            "id",
            "legal",
            "facts",
            "conclusion",
            "relevant_topics",
            "full_legal_memo_original",
            "full_legal_memo_html",
            "created_date",
            "modified_date",
        ]


class HulsburyLawBooksSerializer(serializers.ModelSerializer):
    class Meta:
        model = HulsburyLawBooks
        fields = [
            "book_id",
            "name",
            "statement",
            "citation_list",
            "citation_value",
            "unique_id",
            "created_date",
            "modified_date",
        ]


class RelevantCitationsPassageSerializer(serializers.ModelSerializer):
    class Meta:
        model = RelevantCitationsPassage
        fields = [
            "doc_name",
            "passage",
            "embeddings",
            "score",
            "husbury_file",
            "created_date",
            "modified_date",
        ]


class StatementEmbeddingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatementEmbeddings
        fields = [
            "husbury_file",
            "embeddings",
            "created_date",
            "modified_date",
        ]


class CaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Case
        fields = [
            "id",
            "code",
            "court",
            "judges",
            "petitioner",
            "respondent",
            "citations",
        ]


class CaseparagraphSerializer(serializers.ModelSerializer):
    para_score = serializers.SerializerMethodField()

    def get_para_search(self, instance):
        if instance.para_score:
            return instance.para_score
        return None

    class Meta:
        model = Caseparagraph
        fields = [
            "id",
            "para_count",
            "number",
            "text",
            "case",
            "para_score",
        ]


class CaseNoteSerializer(serializers.ModelSerializer):
    paragraph = CaseparagraphSerializer(read_only=True, many=True)

    class Meta:
        model = CaseNote
        fields = [
            "id",
            "short_text",
            "long_text",
            "para_number",
            "paragraph",
            "case",
            "created_date",
            "modified_date",
        ]


class LegalReaserchParagraphStep1Serializer(serializers.ModelSerializer):
    para_score = serializers.SerializerMethodField()

    def get_para_search(self, instance):
        if instance.para_score:
            instance.para_score = instance.para_score.replace('"', "'")
            return instance.para_score.strip()
        return None

    class Meta:
        model = Caseparagraph
        fields = [
            "id",
            "text",
            "para_score",
        ]


class LegalResearchStep1Serializer(serializers.ModelSerializer):
    ratio_score = serializers.SerializerMethodField()
    case_note_score = serializers.SerializerMethodField()
    case = serializers.SerializerMethodField()
    petitioner_name = serializers.SerializerMethodField()
    respondent_name = serializers.SerializerMethodField()
    court = serializers.SerializerMethodField()
    paragraph_value = LegalReaserchParagraphStep1Serializer(read_only=True, many=True)

    def get_ratio_score(self, instance):
        return instance.ratio_score

    def get_case_note_score(self, instance):
        return instance.case_note_score

    def get_case(self, instance):
        return instance.case.code

    def get_respondent_name(self, instance):
        return instance.case.respondent_name

    def get_petitioner_name(self, instance):
        return instance.case.petitioner_name

    def get_court(self, instance):
        return instance.case.court

    class Meta:
        model = CaseNote
        fields = [
            "id",
            "case",
            "respondent_name",
            "petitioner_name",
            "court",
            "ratio_score",
            "case_note_score",
            "paragraph_value",
        ]
