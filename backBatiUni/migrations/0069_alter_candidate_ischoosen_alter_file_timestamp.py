# Generated by Django 4.0 on 2022-02-16 08:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backBatiUni', '0068_company_amount_company_latitude_company_longitude_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='candidate',
            name='isChoosen',
            field=models.BooleanField(default=None, null=True, verbose_name='Sous traitant selectionné'),
        ),
        migrations.AlterField(
            model_name='file',
            name='timestamp',
            field=models.FloatField(default=1645001396.059864, verbose_name='Timestamp de mise à jour'),
        ),
    ]