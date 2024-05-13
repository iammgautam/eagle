from rest_framework import serializers
from .models import Argument, BriefArgument


class ArgumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Argument
        fields = ["id", "name", "created_date"]


class BriefArgumentSerializer(serializers.ModelSerializer):
    argument = ArgumentSerializer(read_only=True)

    class Meta:
        model = BriefArgument
        fields = [
            "id",
            "legal_principal",
            "factual_analysis",
            "relevant_topics",
            "draft_argument",
            "conclusion",
            "prayer",
            "argument",
            "created_date",
            "modified_date",
        ]
