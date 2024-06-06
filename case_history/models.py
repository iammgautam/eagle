from django.db import models
from django.utils.translation import gettext as _
import uuid
from brief_argument.models import Legal_Memorandum

# Create your models here.
class CaseHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    petitioner_name = models.CharField(verbose_name=_("Petitioner Name"), max_length=255, null=True, blank=True)
    respondent_name = models.CharField(verbose_name=_("Respondent Name"), max_length=255, null=True, blank=True)
    legal_issue = models.TextField(verbose_name=_("Legal Issue"), null=True, blank=True)
    high_court = models.CharField(max_length=255, null=True, blank=True)
    fact_case = models.TextField(verbose_name=_("Fact of the Case"), null=True, blank=True)
    legal_memo = models.OneToOneField(Legal_Memorandum, null=True, blank=True, on_delete=models.CASCADE, related_name="case_history")
    SUBMIT_CHOICES = [
        ('petitioner', _("Petitioner")),
        ('respondent', _('Respondent')),
    ]
    submit_type = models.CharField(max_length=20, null=True, choices=SUBMIT_CHOICES)
    is_completed = models.BooleanField("Is the email sent", default=False, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

class LawTopics(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    token_value = models.IntegerField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    parent = models.ForeignKey("self", null=True, on_delete=models.CASCADE, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.name}'
    
class HighCourts(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)