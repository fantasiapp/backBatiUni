# Generated by Django 4.0.2 on 2022-07-07 08:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backBatiUni', '0008_remove_recommandation_lastworksitedate_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='timestamp',
            field=models.FloatField(default=1657181248.206234, verbose_name='Timestamp de mise à jour'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='timestamp',
            field=models.FloatField(default=1657181248.203893, verbose_name='Timestamp de mise à jour'),
        ),
    ]
