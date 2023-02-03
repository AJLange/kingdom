# Generated by Django 3.2.11 on 2023-02-03 04:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('objects', '0012_character_defaultcharacter_defaultexit_defaultobject_defaultroom_mobject_object'),
    ]

    operations = [
        migrations.CreateModel(
            name='Scene',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField(blank=True, null=True, verbose_name='Scene start time')),
                ('end_time', models.DateTimeField(blank=True, null=True, verbose_name='Scene end time')),
                ('name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Scene display name')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Scene description')),
                ('location', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='scenes_at_location', to='objects.objectdb')),
                ('participants', models.ManyToManyField(blank=True, related_name='scenes_participated', to='objects.ObjectDB')),
            ],
            options={
                'ordering': ['-start_time'],
            },
        ),
        migrations.CreateModel(
            name='LogEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('type', models.IntegerField(choices=[(1, 'Emit'), (2, 'Say'), (3, 'Pose'), (4, 'Dice'), (5, 'Combat')])),
                ('character', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='objects.objectdb')),
                ('scene', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='scenes.scene')),
            ],
        ),
    ]
