# Generated by Django 3.2.11 on 2023-02-05 03:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('objects', '0012_character_defaultcharacter_defaultexit_defaultobject_defaultroom_mobject_object'),
    ]

    operations = [
        migrations.CreateModel(
            name='Squad',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('db_name', models.CharField(max_length=100, verbose_name='Squad Name')),
                ('db_leader', models.CharField(max_length=120, verbose_name='Leader')),
                ('db_orders', models.TextField(blank=True, verbose_name='Orders')),
                ('db_date_created', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='date created')),
                ('db_members', models.ManyToManyField(blank=True, to='objects.ObjectDB')),
            ],
        ),
        migrations.CreateModel(
            name='PlayerGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('db_name', models.CharField(max_length=100, verbose_name='Group Name')),
                ('db_leader', models.CharField(max_length=120, verbose_name='Leader')),
                ('db_description', models.TextField(blank=True, verbose_name='Description')),
                ('db_color', models.CharField(max_length=20, verbose_name='Color')),
                ('db_radio_a', models.CharField(max_length=10, verbose_name='Radio A')),
                ('db_radio_b', models.CharField(max_length=10, verbose_name='Radio B')),
                ('db_motd', models.TextField(blank=True, verbose_name='Message of the Day')),
                ('db_date_created', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='date created')),
                ('db_members', models.ManyToManyField(blank=True, to='objects.ObjectDB')),
                ('db_squads', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='groups.squad')),
            ],
        ),
    ]
