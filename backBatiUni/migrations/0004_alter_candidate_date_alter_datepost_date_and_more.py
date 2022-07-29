# Generated by Django 4.0.2 on 2022-07-29 14:15

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('backBatiUni', '0003_alter_candidate_date_alter_datepost_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='candidate',
            name='date',
            field=models.DateField(default=datetime.datetime(2022, 7, 29, 14, 15, 11, 869179, tzinfo=utc), verbose_name="Date de candidature ou date d'acceptation"),
        ),
        migrations.AlterField(
            model_name='datepost',
            name='date',
            field=models.DateField(default=datetime.datetime(2022, 7, 29, 14, 15, 11, 868236, tzinfo=utc), verbose_name='Date du chantier'),
        ),
        migrations.AlterField(
            model_name='file',
            name='timestamp',
            field=models.FloatField(default=1659104111.871258, verbose_name='Timestamp de mise à jour'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='timestamp',
            field=models.FloatField(default=1659104111.868694, verbose_name='Timestamp de mise à jour'),
        ),
        migrations.AlterField(
            model_name='post',
            name='creationDate',
            field=models.DateField(default=datetime.datetime(2022, 7, 29, 14, 15, 11, 866777, tzinfo=utc), verbose_name="Date de creation de l'annonce"),
        ),
    ]
