# Generated by Django 5.0.4 on 2024-05-22 07:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('case_history', '0007_highcourts'),
    ]

    operations = [
        migrations.AddField(
            model_name='casehistory',
            name='high_court',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
