from django.db import models
from django.utils.translation import gettext as _
import uuid

class Legal_Memorandum(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    legal = models.TextField(null=True, blank=True)
    facts = models.TextField(null=True, blank=True)
    conclusion = models.TextField(null=True, blank=True)
    relevant_topics = models.TextField(null=True, blank=True)
    full_legal_memo_original = models.TextField(null=True, blank=True)
    full_legal_memo_html = models.TextField(null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

class Argument(models.Model):
    title = models.TextField(null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    detailed_content = models.TextField(null=True, blank=True)
    legal_memo = models.ForeignKey(Legal_Memorandum, on_delete=models.CASCADE,null=True,blank=True,related_name="analysis")
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

class AIB_EXAM(models.Model):
    question = models.TextField(null=True, blank=True)
    option_a = models.TextField(null=True, blank=True)
    option_b = models.TextField(null=True, blank=True)
    option_c = models.TextField(null=True, blank=True)
    option_d = models.TextField(null=True, blank=True)
    answer = models.TextField(null=True, blank=True)
    relevant_topics_content = models.TextField(null=True, blank=True)
    is_completed = models.BooleanField("Is the email sent", default=False, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)