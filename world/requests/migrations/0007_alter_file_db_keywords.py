# Generated by Django 3.2.11 on 2023-03-02 01:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('requests', '0006_auto_20230301_2021'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='db_keywords',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='requests.keyword'),
        ),
    ]
