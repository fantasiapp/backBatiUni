# Generated by Django 4.0.2 on 2022-05-12 15:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backBatiUni', '0046_alter_file_timestamp_alter_notification_timestamp'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='boostTimestamp',
            field=models.FloatField(default=1652371111.477477, verbose_name='Timestamp de mise à jour'),
        ),
        migrations.AddField(
            model_name='post',
            name='isBoosted',
            field=models.BooleanField(default=False, verbose_name='Détermine si une annonce est boosté'),
        ),
        migrations.AlterField(
            model_name='file',
            name='timestamp',
            field=models.FloatField(default=1652371111.480877, verbose_name='Timestamp de mise à jour'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='timestamp',
            field=models.FloatField(default=1652371111.478742, verbose_name='Timestamp de mise à jour'),
        ),
    ]