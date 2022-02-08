# Generated by Django 4.0 on 2022-02-04 13:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backBatiUni', '0035_rename_latitude_post_lattitude_alter_files_timestamp'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='unitOfTime',
            field=models.CharField(default='Prix Journalier', max_length=128, null=True, verbose_name='Unité de temps'),
        ),
        migrations.AlterField(
            model_name='files',
            name='timestamp',
            field=models.FloatField(default=1643982745.029638, verbose_name='Timestamp de mise à jour'),
        ),
    ]