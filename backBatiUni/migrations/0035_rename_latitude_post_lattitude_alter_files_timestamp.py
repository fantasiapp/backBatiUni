# Generated by Django 4.0 on 2022-02-04 10:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backBatiUni', '0034_alter_files_timestamp_alter_post_latitude_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='post',
            old_name='latitude',
            new_name='lattitude',
        ),
        migrations.AlterField(
            model_name='files',
            name='timestamp',
            field=models.FloatField(default=1643971271.728962, verbose_name='Timestamp de mise à jour'),
        ),
    ]