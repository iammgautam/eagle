from django.contrib import admin
from django.utils.translation import gettext as _
from .models import CaseHistory, LawTopics, HighCourts


# Register your models here.
@admin.register(CaseHistory)
class CaseHistoryAdmin(admin.ModelAdmin):
    list_display = ("id","legal_issue")
    list_filter = (
        "created_date",
        "modified_date",
    )
    search_fields = (
        "legal_issue",
    )
    ordering = ("-created_date",)

class ParentList(admin.SimpleListFilter):
    title = _("Parent Filters")
    parameter_name = "parent__name"

    def lookups(self, request, model_admin):
        return [
            ("True", _("All Parent Law")),
            ("CPC", _("CPC")),
            ("Labour Law", _("Labour Law")),
            ("Constitutional Law", _("Constitutional Law")),
            ("Contract Law", _("Contract Law")),
            ("Law of Evidence", _("Law of Evidence")),
            ("Competition Law", _("Competition Law")),
            ("Taxation Laws", _("Taxation Laws")),
            ("Property Law", _("Property Law")),
            ("Intellectual Property Law", _("Intellectual Property Law")),
            ("Family Law - 1", _("Family Law - 1")),
            ("Law of Crimes - 3", _("Law of Crimes - 3")),
        ]

    def queryset(self, request, queryset):
        if self.value() == "True":
            return queryset.filter(parent__isnull=True)
        if self.value() == "CPC":
            return queryset.filter(parent__name="CPC")
        if self.value() == "Labour Law":
            return queryset.filter(parent__name="Labour Law")
        if self.value() == "Constitutional Law":
            return queryset.filter(parent__name="Constitutional Law")
        if self.value() == "Contract Law":
            return queryset.filter(parent__name="Contract Law")
        if self.value() == "Law of Evidence":
            return queryset.filter(parent__name="Law of Evidence")
        if self.value() == "Competition Law":
            return queryset.filter(parent__name="Competition Law")
        if self.value() == "Taxation Laws":
            return queryset.filter(parent__name="Taxation Laws")
        if self.value() == "Property Law":
            return queryset.filter(parent__name="Property Law")
        if self.value() == "Intellectual Property Law":
            return queryset.filter(parent__name="Intellectual Property Law")
        if self.value() == "Family Law - 1":
            return queryset.filter(parent__name="Family Law - 1")
        if self.value() == "Law of Crimes - 3":
            return queryset.filter(parent__name="Law of Crimes - 3")

@admin.register(LawTopics)
class LawTopicsAdmin(admin.ModelAdmin):
    list_display = ("id", "parent", "name")
    list_filter = ("created_date", "modified_date", ParentList)
    search_fields = (
        "name",
        "parent",
    )
    ordering = ("-created_date",)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "parent":
            kwargs["queryset"] = LawTopics.objects.filter(parent__isnull=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(HighCourts)
class HghiCourtsAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    list_filter = ("created_date", "modified_date")
    search_fields = ("name",)
    ordering = ("-created_date",)
