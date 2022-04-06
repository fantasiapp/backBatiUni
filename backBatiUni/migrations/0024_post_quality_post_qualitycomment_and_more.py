# Generated by Django 4.0.2 on 2022-04-03 12:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backBatiUni', '0023_candidate_contact_alter_file_timestamp'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='quality',
            field=models.IntegerField(default=1, verbose_name='Qualité du travail fourni'),
        ),
        migrations.AddField(
            model_name='post',
            name='qualityComment',
            field=models.TextField(default='', verbose_name='Qualité du travail fourni Commentaire'),
        ),
        migrations.AlterField(
            model_name='file',
            name='timestamp',
            field=models.FloatField(default=1648990018.66507, verbose_name='Timestamp de mise à jour'),
        ),
    ]