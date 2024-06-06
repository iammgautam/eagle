from rest_framework import serializers
from .models import Argument, Legal_Memorandum, AIB_EXAM


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
