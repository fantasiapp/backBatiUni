# Generated by Django 4.0.2 on 2022-05-24 17:36

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('backBatiUni', '0054_alter_file_timestamp_alter_notification_timestamp_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='creationDate',
            field=models.DateField(default=django.utils.timezone.now, verbose_name="Date de creation de l'annonce"),
        ),
        migrations.AlterField(
            model_name='file',
            name='timestamp',
            field=models.FloatField(default=1653413760.089344, verbose_name='Timestamp de mise à jour'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='timestamp',
            field=models.FloatField(default=1653413760.087152, verbose_name='Timestamp de mise à jour'),
        ),
        migrations.AlterField(
            model_name='post',
            name='boostTimestamp',
            field=models.FloatField(default=1653413760.085834, verbose_name='Timestamp de mise à jour'),
        ),
    ]
