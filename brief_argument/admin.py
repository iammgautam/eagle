from django.contrib import admin
from .models import Argument, BriefArgument

# Register your models here.
@admin.register(Argument)
class ArgumentAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_date')
    list_filter = ('created_date',)
    search_fields = ('name',)

@admin.register(BriefArgument)
class BriefArgumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'legal_principal', 'created_date', 'modified_date')
    list_filter = ('created_date', 'modified_date', 'relevant_topics')
    search_fields = ('legal_principal',)