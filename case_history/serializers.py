from rest_framework import serializers
from .models import CaseHistory
from brief_argument.models import BriefArgument
from brief_argument.serializers import BriefArgumentSerializer


class CaseHistorySerializer(serializers.ModelSerializer):
    brief_argument = BriefArgumentSerializer(read_only=True)

    class Meta:
        model = CaseHistory
        fields = [
            "id",
            "petitioner_name",
            "respodent_name",
            "legal_isse",
            "fact_case",
            "brief_argument",
            "created_date",
            "modified_date",
        ]
