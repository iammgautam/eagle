from django.contrib import admin
from .models import CaseHistory, LawTopics, HighCourts


# Register your models here.
@admin.register(CaseHistory)
class CaseHistoryAdmin(admin.ModelAdmin):
    list_display = ("id", "petitioner_name", "respondent_name", "high_court")
    list_filter = ("created_date", "modified_date", "petitioner_name", "respondent_name", "high_court")
    search_fields = (
        "legal_principal",
        "petitioner_name",
        "respondent_name",
        "legal_issue",
        "fact_case",
        "brief_argument",
        "high_court",
    )
    ordering = ('-created_date',)

@admin.register(LawTopics)
class LawTopicsAdmin(admin.ModelAdmin):
    list_display = ("id", "parent", "name")
    list_filter = ("created_date", "modified_date", "parent")
    search_fields = (
        "name",
        "parent",
    )
    ordering = ('-created_date',)


@admin.register(HighCourts)
class HghiCourtsAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    list_filter = ("created_date", "modified_date")
    search_fields = (
        "name",
    )
    ordering = ('-created_date',)
