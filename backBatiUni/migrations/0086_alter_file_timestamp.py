# Generated by Django 4.0.2 on 2022-02-23 14:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backBatiUni', '0085_viewpost_alter_favoritepost_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='timestamp',
            field=models.FloatField(default=1645628060.072186, verbose_name='Timestamp de mise à jour'),
        ),
    ]
