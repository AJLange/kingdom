# Generated by Django 3.2.11 on 2023-02-06 17:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='roster',
            name='lock_storage',
            field=models.TextField(blank=True, help_text='defined in setup_utils', verbose_name='locks'),
        ),
    ]
