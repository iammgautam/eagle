from rest_framework import serializers
from .models import CaseHistory, HighCourts
from brief_argument.serializers import BriefArgumentSerializer


class CaseHistorySerializer(serializers.ModelSerializer):
    brief_argument = BriefArgumentSerializer(read_only=True)

    class Meta:
        model = CaseHistory
        fields = [
            "id",
            "petitioner_name",
            "respondent_name",
            "legal_issue",
            "fact_case",
            "high_court",
            "brief_argument",
            "is_completed",
            "submit_type",
            "created_date",
            "modified_date",
        ]

class HighCourtsSerializer(serializers.ModelSerializer):
    class Meta:
        model = HighCourts
        fields = ["id", "name", "created_date"]