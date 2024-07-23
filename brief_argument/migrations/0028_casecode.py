# Generated by Django 5.0.4 on 2024-07-19 11:29

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('brief_argument', '0027_cocounsel_scrape_link'),
    ]

    operations = [
        migrations.CreateModel(
            name='CaseCode',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('case_code', models.TextField()),
                ('case', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='brief_argument.case')),
            ],
            options={
                'db_table': 'case_codes',
            },
        ),
    ]