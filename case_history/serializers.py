from rest_framework import serializers
from .models import CaseHistory, HighCourts, LegalSearchHistory


class CaseHistorySerializer(serializers.ModelSerializer):

    class Meta:
        model = CaseHistory
        fields = [
            "id",
            "legal_issue",
            "fact_case",
            "legal_memo",
            "unique_id",
            "is_completed",
            "legal_research",
            "created_date",
            "modified_date",
        ]

class HighCourtsSerializer(serializers.ModelSerializer):
    class Meta:
        model = HighCourts
        fields = ["id", "name", "created_date"]


class LegalSearchHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = LegalSearchHistory
        fields = ["id", "search_text", "embeddings", "created_date"]