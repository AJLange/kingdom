# Generated by Django 3.2.11 on 2023-03-02 01:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('requests', '0003_request_db_is_open'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='file',
            name='db_keywords',
        ),
        migrations.AddField(
            model_name='file',
            name='db_keywords',
            field=models.ManyToManyField(blank=True, null=True, to='requests.Keyword'),
        ),
    ]
