# Generated by Django 4.0 on 2022-02-08 15:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backBatiUni', '0054_candidate_company_alter_files_timestamp_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='files',
            name='timestamp',
            field=models.FloatField(default=1644332643.013984, verbose_name='Timestamp de mise à jour'),
        ),
    ]