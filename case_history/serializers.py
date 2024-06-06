from rest_framework import serializers
from .models import CaseHistory, HighCourts


class CaseHistorySerializer(serializers.ModelSerializer):

    class Meta:
        model = CaseHistory
        fields = [
            "id",
            "petitioner_name",
            "respondent_name",
            "legal_issue",
            "fact_case",
            "high_court",
            "legam_memo",
            "is_completed",
            "submit_type",
            "created_date",
            "modified_date",
        ]

class HighCourtsSerializer(serializers.ModelSerializer):
    class Meta:
        model = HighCourts
        fields = ["id", "name", "created_date"]