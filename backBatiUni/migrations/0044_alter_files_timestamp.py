# Generated by Django 4.0 on 2022-02-08 09:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backBatiUni', '0043_alter_files_timestamp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='files',
            name='timestamp',
            field=models.FloatField(default=1644313236.205376, verbose_name='Timestamp de mise à jour'),
        ),
    ]