from django.contrib import admin
from .models import CaseHistory, LawTopics


# Register your models here.
@admin.register(CaseHistory)
class CaseHistoryAdmin(admin.ModelAdmin):
    list_display = ("id", "petitioner_name", "respondent_name")
    list_filter = ("created_date", "modified_date", "petitioner_name", "respondent_name")
    search_fields = (
        "legal_principal",
        "petitioner_name",
        "respondent_name",
        "legal_issue",
        "fact_case",
        "brief_argument",
    )

@admin.register(LawTopics)
class LawTopicsAdmin(admin.ModelAdmin):
    list_display = ("id", "parent", "name")
    list_filter = ("created_date", "modified_date", "parent")
    search_fields = (
        "name",
        "parent",
    )
