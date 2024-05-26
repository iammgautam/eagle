from django.db import models
from django.utils.translation import gettext as _
import uuid

class Argument(models.Model):
    title = models.TextField(null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)

class BriefArgument(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    legal_principal = models.TextField(null=True, blank=True)
    factual_analysis = models.TextField(null=True, blank=True)
    case_name = models.TextField(null=True, blank=True)
    relevant_topics = models.TextField(null=True, blank=True)
    draft_argument = models.TextField(null=True, blank=True)
    introduction = models.TextField(null=True, blank=True)
    conclusion = models.TextField(null=True, blank=True)
    title = models.TextField(null=True, blank=True)
    prayer = models.TextField(null=True, blank=True)
    argument_value = models.ManyToManyField(Argument, related_name="brief_argument")
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
