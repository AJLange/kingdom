# Generated by Django 3.2.11 on 2023-02-06 22:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0002_auto_20230206_1745'),
    ]

    operations = [
        migrations.AlterField(
            model_name='playergroup',
            name='db_twoic',
            field=models.CharField(blank=True, max_length=120, null=True, verbose_name='Secondary Leader'),
        ),
    ]
