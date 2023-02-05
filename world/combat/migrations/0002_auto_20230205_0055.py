# Generated by Django 3.2.11 on 2023-02-05 05:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('combat', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='weapon',
            name='db_flag_1',
            field=models.IntegerField(blank=True, choices=[(1, 'Megablast'), (2, 'Exceed'), (3, 'Priority'), (4, 'Stable'), (5, 'Blind'), (6, 'Degrade'), (7, 'Entangle')], null=True),
        ),
        migrations.AlterField(
            model_name='weapon',
            name='db_flag_2',
            field=models.IntegerField(blank=True, choices=[(1, 'Megablast'), (2, 'Exceed'), (3, 'Priority'), (4, 'Stable'), (5, 'Blind'), (6, 'Degrade'), (7, 'Entangle')], null=True),
        ),
        migrations.AlterField(
            model_name='weapon',
            name='db_type_2',
            field=models.IntegerField(blank=True, choices=[(1, 'Slashing'), (2, 'Piercing'), (3, 'Electric'), (4, 'Explosive'), (5, 'Fire'), (6, 'Gravity'), (7, 'Air'), (8, 'Ice'), (9, 'Toxic'), (10, 'Blunt'), (11, 'Quake'), (12, 'Karate'), (13, 'Sonic'), (14, 'Time'), (15, 'Wood'), (16, 'Water'), (17, 'Plasma'), (18, 'Laser'), (19, 'Light'), (20, 'Darkness'), (21, 'Psycho'), (22, 'Chi'), (23, 'Disenchant')], null=True),
        ),
        migrations.AlterField(
            model_name='weapon',
            name='db_type_3',
            field=models.IntegerField(blank=True, choices=[(1, 'Slashing'), (2, 'Piercing'), (3, 'Electric'), (4, 'Explosive'), (5, 'Fire'), (6, 'Gravity'), (7, 'Air'), (8, 'Ice'), (9, 'Toxic'), (10, 'Blunt'), (11, 'Quake'), (12, 'Karate'), (13, 'Sonic'), (14, 'Time'), (15, 'Wood'), (16, 'Water'), (17, 'Plasma'), (18, 'Laser'), (19, 'Light'), (20, 'Darkness'), (21, 'Psycho'), (22, 'Chi'), (23, 'Disenchant')], null=True),
        ),
    ]
