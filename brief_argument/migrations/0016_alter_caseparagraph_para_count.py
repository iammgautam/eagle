# Generated by Django 5.0.4 on 2024-06-21 10:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('brief_argument', '0015_remove_casenote_embeddings_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='caseparagraph',
            name='para_count',
            field=models.CharField(blank=True, null=True),
        ),
    ]