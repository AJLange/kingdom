# Generated by Django 3.2.11 on 2023-03-12 21:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0003_alter_playergroup_db_twoic'),
        ('boards', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='bulletinboard',
            name='db_groups',
            field=models.ManyToManyField(blank=True, to='groups.PlayerGroup'),
        ),
    ]