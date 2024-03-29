# Generated by Django 3.2.11 on 2023-03-11 22:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('combat', '0001_initial'),
        ('armor', '0003_alter_armormode_db_capabilities'),
    ]

    operations = [
        migrations.AddField(
            model_name='armormode',
            name='db_busterlist',
            field=models.ManyToManyField(blank=True, to='combat.BusterList'),
        ),
        migrations.AddField(
            model_name='armormode',
            name='db_weapons',
            field=models.ManyToManyField(blank=True, to='combat.Weapon'),
        ),
    ]
