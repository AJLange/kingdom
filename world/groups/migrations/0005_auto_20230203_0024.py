# Generated by Django 3.2.11 on 2023-02-03 05:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0004_auto_20230202_1707'),
    ]

    operations = [
        migrations.AlterField(
            model_name='playergroup',
            name='db_key',
            field=models.CharField(db_index=True, max_length=80),
        ),
        migrations.AlterField(
            model_name='squad',
            name='db_key',
            field=models.CharField(db_index=True, max_length=100),
        ),
    ]
