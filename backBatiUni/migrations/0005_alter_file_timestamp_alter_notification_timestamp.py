# Generated by Django 4.0.2 on 2022-07-07 10:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backBatiUni', '0004_company_role_company_activity_company_address_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='timestamp',
            field=models.FloatField(default=1657190719.70397, verbose_name='Timestamp de mise à jour'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='timestamp',
            field=models.FloatField(default=1657190719.701765, verbose_name='Timestamp de mise à jour'),
        ),
    ]
