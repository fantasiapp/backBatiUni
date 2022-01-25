# Generated by Django 4.0 on 2022-01-25 18:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backBatiUni', '0020_post_address_alter_files_timestamp_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='contactName',
            field=models.CharField(default=None, max_length=256, null=True, verbose_name='Nom du contact responsable de l’app'),
        ),
        migrations.AlterField(
            model_name='files',
            name='timestamp',
            field=models.FloatField(default=1643135066.700651, verbose_name='Timestamp de mise à jour'),
        ),
    ]
