from django.contrib import admin
from .models import Argument, Legal_Memorandum, AIB_EXAM


# Register your models here.
@admin.register(Argument)
class ArgumentAdmin(admin.ModelAdmin):
    list_display = ("content", "created_date")
    list_filter = ("created_date",)
    search_fields = ("content",)


@admin.register(AIB_EXAM)
class AIB_EXAMAdmin(admin.ModelAdmin):
    list_display = (
        "question",
        "option_a",
        "option_b",
        "option_c",
        "option_d",
        "answer",
        "is_completed",
        "created_date",
    )
    list_filter = ("is_completed",)
    search_fields = ("question",)


@admin.register(Legal_Memorandum)
class Legal_MemorandumAdmin(admin.ModelAdmin):
    list_display = ("id", "created_date", "modified_date")
    list_filter = (
        "created_date",
        "modified_date",
    )
    search_fields = ("legal_principal",)
    ordering = ("-created_date",)
