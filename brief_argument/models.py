from django.db import models
from django.utils.translation import gettext as _
import uuid
# from case_history.models import CaseHistory

# Create your models here.
class Argument(models.Model):
    name = models.TextField(max_length=255, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)

class BriefArgument(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    legal_principal = models.TextField(null=True, blank=True)
    factual_analysis = models.TextField(null=True, blank=True)
    relevant_topics = models.TextField(null=True, blank=True)
    draft_argument = models.TextField(null=True, blank=True)
    conclusion = models.TextField(null=True, blank=True)
    prayer = models.TextField(null=True, blank=True)
    argument = models.ForeignKey(Argument, on_delete=models.CASCADE, null=True, blank=True, related_name="brief_argument")
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
