# Generated by Django 4.0.2 on 2022-02-22 11:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backBatiUni', '0076_alter_file_timestamp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='timestamp',
            field=models.FloatField(default=1645527962.88907, verbose_name='Timestamp de mise à jour'),
        ),
    ]