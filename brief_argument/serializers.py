from rest_framework import serializers
from .models import Argument, BriefArgument


class ArgumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Argument
        fields = ["id", "title", "content", "created_date"]


class BriefArgumentSerializer(serializers.ModelSerializer):
    argument_value = ArgumentSerializer(read_only=True, many=True)
    class Meta:
        model = BriefArgument
        fields = [
            "id",
            "legal_principal",
            "factual_analysis",
            "case_name",
            "relevant_topics",
            "draft_argument",
            "introduction",
            "conclusion",
            "title",
            "prayer",
            "created_date",
            "modified_date",
            "argument_value",
        ]