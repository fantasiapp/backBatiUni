# Generated by Django 4.0.2 on 2022-05-13 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backBatiUni', '0047_post_boosttimestamp_post_isboosted_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='timestamp',
            field=models.FloatField(default=1652451194.70711, verbose_name='Timestamp de mise à jour'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='timestamp',
            field=models.FloatField(default=1652451194.704902, verbose_name='Timestamp de mise à jour'),
        ),
        migrations.AlterField(
            model_name='post',
            name='boostTimestamp',
            field=models.FloatField(default=1652451194.703563, verbose_name='Timestamp de mise à jour'),
        ),
    ]