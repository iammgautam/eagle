from django.contrib import admin
from .models import (
    Argument,
    Legal_Memorandum,
    AIB_EXAM,
    HulsburyLawBooks,
    RelevantCitationsPassage,
    StatementEmbeddings,
    Case,CaseNote, Caseparagraph
)


# Register your models here.
@admin.register(Argument)
class ArgumentAdmin(admin.ModelAdmin):
    list_display = ("title", "created_date")
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


@admin.register(HulsburyLawBooks)
class HulsburyLawBooksAdmin(admin.ModelAdmin):
    list_display = ("id", "book_id", "name")
    list_filter = (
        "created_date",
        "modified_date",
    )
    search_fields = ("book_id", "name")
    ordering = ("book_id",)


@admin.register(RelevantCitationsPassage)
class RelevantCitationsPassageAdmin(admin.ModelAdmin):
    list_display = ("id", "husbury_file", "doc_name")
    list_filter = (
        "created_date",
        "modified_date",
    )
    search_fields = ("doc_name",)


@admin.register(StatementEmbeddings)
class StatementEmbeddingsAdmin(admin.ModelAdmin):
    list_display = ("id", "husbury_file",)
    list_filter = (
        "created_date",
        "modified_date",
    )
    search_fields = ("husbury_file",)


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ("id", "code",)
    list_filter = (
        "created_date",
        "modified_date",
    )
    search_fields = ("code",)


@admin.register(CaseNote)
class CaseNoteAdmin(admin.ModelAdmin):
    list_display = ("id", "case",)
    list_filter = (
        "created_date",
        "modified_date",
    )
    search_fields = ("case","short_text")


@admin.register(Caseparagraph)
class CaseparagraphAdmin(admin.ModelAdmin):
    list_display = ("id", "case",)
    list_filter = (
        "created_date",
        "modified_date",
    )
    search_fields = ("case","text")
