# Generated by Django 3.2.11 on 2023-03-14 21:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('objects', '0012_character_defaultcharacter_defaultexit_defaultobject_defaultroom_mobject_object'),
        ('boards', '0003_alter_boardpost_db_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='bulletinboard',
            name='has_subscriber',
            field=models.ManyToManyField(blank=True, to='objects.ObjectDB'),
        ),
    ]
