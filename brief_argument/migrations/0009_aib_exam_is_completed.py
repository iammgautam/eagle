# Generated by Django 5.0.4 on 2024-06-06 09:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('brief_argument', '0008_aib_exam'),
    ]

    operations = [
        migrations.AddField(
            model_name='aib_exam',
            name='is_completed',
            field=models.BooleanField(blank=True, default=False, verbose_name='Is the email sent'),
        ),
    ]