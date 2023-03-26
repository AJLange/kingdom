# Generated by Django 3.2.11 on 2023-03-26 20:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('objects', '0012_character_defaultcharacter_defaultexit_defaultobject_defaultroom_mobject_object'),
        ('boards', '0004_bulletinboard_has_subscriber'),
    ]

    operations = [
        migrations.AddField(
            model_name='boardpost',
            name='read_by',
            field=models.ManyToManyField(blank=True, to='objects.ObjectDB'),
        ),
        migrations.AddField(
            model_name='bulletinboard',
            name='db_timeout',
            field=models.IntegerField(blank=True, default=180, verbose_name='Timeout'),
        ),
        migrations.AlterField(
            model_name='boardpost',
            name='db_title',
            field=models.CharField(max_length=360, verbose_name='Post Title'),
        ),
    ]