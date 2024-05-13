from django.db import models
from django.utils.translation import gettext as _
import uuid
from brief_argument.models import BriefArgument

# Create your models here.
class CaseHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    petitioner_name = models.CharField(verbose_name=_("Petitioner Name"), max_length=255, null=True, blank=True)
    respodent_name = models.CharField(verbose_name=_("Respondent Name"), max_length=255, null=True, blank=True)
    legal_isse = models.TextField(verbose_name=_("Legal Issue"), null=True, blank=True)
    fact_case = models.TextField(verbose_name=_("Fact of the Case"), null=True, blank=True)
    brief_argument = models.OneToOneField(BriefArgument, on_delete=models.CASCADE,related_name="case_history")
    SUBMIT_CHOICES = [
        ('petitioner', _("Petitioner")),
        ('respondent', _('Respondent')),
    ]
    submit_type = models.CharField(max_length=20, null=True, choices=SUBMIT_CHOICES)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)