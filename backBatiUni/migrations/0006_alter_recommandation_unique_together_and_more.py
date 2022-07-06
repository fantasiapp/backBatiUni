# Generated by Django 4.0.2 on 2022-07-04 08:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backBatiUni', '0005_alter_file_timestamp_alter_notification_timestamp_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='recommandation',
            unique_together=set(),
        ),
        migrations.AlterField(
            model_name='file',
            name='timestamp',
            field=models.FloatField(default=1656925010.427643, verbose_name='Timestamp de mise à jour'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='timestamp',
            field=models.FloatField(default=1656925010.42543, verbose_name='Timestamp de mise à jour'),
        ),
    ]