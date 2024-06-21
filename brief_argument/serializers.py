from rest_framework import serializers
from .models import (
    Argument,
    Legal_Memorandum,
    AIB_EXAM,
    HulsburyLawBooks,
    RelevantCitationsPassage,
    StatementEmbeddings,
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
