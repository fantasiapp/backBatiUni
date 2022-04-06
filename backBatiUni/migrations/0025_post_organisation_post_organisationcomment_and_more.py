# Generated by Django 4.0.2 on 2022-04-03 14:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backBatiUni', '0024_post_quality_post_qualitycomment_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='organisation',
            field=models.IntegerField(default=1, verbose_name='Organisation fourni'),
        ),
        migrations.AddField(
            model_name='post',
            name='organisationComment',
            field=models.TextField(default='', verbose_name='Organisation Commentaire'),
        ),
        migrations.AddField(
            model_name='post',
            name='security',
            field=models.IntegerField(default=1, verbose_name='Respect de la sécurité et de la propreté du chantier'),
        ),
        migrations.AddField(
            model_name='post',
            name='securityComment',
            field=models.TextField(default='', verbose_name='Respect de la sécurité et de la propreté du chantier Commentaire'),
        ),
        migrations.AlterField(
            model_name='file',
            name='timestamp',
            field=models.FloatField(default=1648995457.188456, verbose_name='Timestamp de mise à jour'),
        ),
    ]