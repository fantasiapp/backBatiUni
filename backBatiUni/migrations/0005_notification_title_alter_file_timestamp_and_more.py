# Generated by Django 4.0.2 on 2022-06-09 10:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backBatiUni', '0004_userprofile_tokennotification_alter_file_timestamp_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='title',
            field=models.CharField(default='Titre par défaut', max_length=128, verbose_name='Nature de la notification'),
        ),
        migrations.AlterField(
            model_name='file',
            name='timestamp',
            field=models.FloatField(default=1654770194.916506, verbose_name='Timestamp de mise à jour'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='timestamp',
            field=models.FloatField(default=1654770194.91438, verbose_name='Timestamp de mise à jour'),
        ),
        migrations.AlterField(
            model_name='post',
            name='boostTimestamp',
            field=models.FloatField(default=1654770194.913011, verbose_name='Timestamp de mise à jour'),
        ),
    ]
