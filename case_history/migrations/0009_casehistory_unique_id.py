# Generated by Django 5.0.4 on 2024-07-12 14:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('case_history', '0008_legalsearchhistory'),
    ]

    operations = [
        migrations.AddField(
            model_name='casehistory',
            name='unique_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
