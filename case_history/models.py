from django.db import models
from pgvector.django import VectorField
from django.utils.translation import gettext as _
import uuid
from brief_argument.models import Legal_Memorandum

# Create your models here.
class CaseHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    legal_issue = models.TextField(verbose_name=_("Legal Issue"), null=True, blank=True)
    fact_case = models.TextField(verbose_name=_("Fact of the Case"), null=True, blank=True)
    legal_research = models.TextField(verbose_name=_("Legal Research"), null=True, blank=True)
    legal_memo = models.OneToOneField(Legal_Memorandum, null=True, blank=True, on_delete=models.CASCADE, related_name="case_history")
    unique_id = models.IntegerField(null=True, blank=True)
    is_completed = models.BooleanField("Is the email sent", default=False, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

class LawTopics(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    token_value = models.IntegerField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    parent = models.ForeignKey("self", null=True, on_delete=models.CASCADE, blank=True)
    topic_id = models.CharField(null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.name}'
    
class HighCourts(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)


class LegalSearchHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    search_text = models.TextField(null=True, blank=True)
    embeddings = VectorField(dimensions=3072)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)