from django.contrib import admin
from .models import CaseHistory


# Register your models here.
@admin.register(CaseHistory)
class CaseHistoryAdmin(admin.ModelAdmin):
    list_display = ("id", "petitioner_name", "respodent_name")
    list_filter = ("created_date", "modified_date", "petitioner_name", "respodent_name")
    search_fields = (
        "legal_principal",
        "petitioner_name",
        "respodent_name",
        "legal_isse",
        "fact_case",
        "brief_argument",
    )
