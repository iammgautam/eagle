# Generated by Django 5.0.4 on 2024-06-29 19:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('brief_argument', '0020_legal_memorandum_question_legal_memorandum_sof'),
    ]

    operations = [
        migrations.AddField(
            model_name='legal_memorandum',
            name='decision_conclusion',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='legal_memorandum',
            name='decision_intro',
            field=models.TextField(blank=True, null=True),
        ),
    ]
