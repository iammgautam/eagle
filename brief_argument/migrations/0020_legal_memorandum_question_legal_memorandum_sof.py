# Generated by Django 5.0.4 on 2024-06-28 20:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('brief_argument', '0019_casenote_cohere_embed'),
    ]

    operations = [
        migrations.AddField(
            model_name='legal_memorandum',
            name='question',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='legal_memorandum',
            name='sof',
            field=models.TextField(blank=True, null=True),
        ),
    ]
