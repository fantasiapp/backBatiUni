# Generated by Django 4.0.2 on 2022-07-04 08:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backBatiUni', '0002_alter_file_timestamp_alter_notification_timestamp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='timestamp',
            field=models.FloatField(default=1656922424.532372, verbose_name='Timestamp de mise à jour'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='timestamp',
            field=models.FloatField(default=1656922424.530137, verbose_name='Timestamp de mise à jour'),
        ),
    ]