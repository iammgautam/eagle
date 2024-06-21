from django.db import models
from pgvector.django import VectorField
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
    legal_memo = models.ForeignKey(
        Legal_Memorandum,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="analysis",
    )
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


class HulsburyLawBooks(models.Model):
    book_id = models.CharField(null=True, blank=True)
    name = models.CharField(null=True, blank=True)
    statement = models.TextField(null=True, blank=True)
    citation_list = models.TextField(null=True, blank=True)
    citation_value = models.TextField(null=True, blank=True)
    unique_id = models.CharField(null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)


class RelevantCitationsPassage(models.Model):
    doc_name = models.TextField(null=True, blank=True)
    passage = models.TextField(null=True, blank=True)
    embeddings = VectorField(dimensions=3072)
    score = models.TextField(null=True, blank=True)
    husbury_file = models.ForeignKey(
        HulsburyLawBooks,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="relevant_passage",
    )
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)


class StatementEmbeddings(models.Model):
    husbury_file = models.OneToOneField(
        HulsburyLawBooks,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="statement_embeddings",
    )
    embeddings = VectorField(dimensions=3072)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)


class Case(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.TextField(null=True, blank=True)
    court = models.CharField(null=True, blank=True)
    judges = models.TextField(null=True, blank=True)
    petitioner = models.CharField(null=True, blank=True)
    respondent = models.CharField(null=True, blank=True)
    citations = models.JSONField(default=dict, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)


class Caseparagraph(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    para_count = models.CharField(null=True, blank=True)
    number = models.CharField(null=True, blank=True)
    text = models.TextField(null=True, blank=True)
    # embeddings = VectorField(dimensions=3072)
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name="paragraph")
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)


class CaseNote(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    short_text = models.TextField(null=True, blank=True)
    long_text = models.TextField(null=True, blank=True)
    # embeddings = VectorField(dimensions=3072)
    para_number = models.CharField(null=True, blank=True)
    paragraph = models.ManyToManyField(Caseparagraph, related_name="case_note")
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name="case_note")
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
