# Generated by Django 5.0.4 on 2024-06-06 08:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('brief_argument', '0005_argument_detailed_content_detailedanalysis'),
    ]

    operations = [
        migrations.RenameField(
            model_name='legal_memorandum',
            old_name='full_legal_memo',
            new_name='full_legal_memo_html',
        ),
        migrations.AddField(
            model_name='legal_memorandum',
            name='full_legal_memo_original',
            field=models.TextField(blank=True, null=True),
        ),
    ]