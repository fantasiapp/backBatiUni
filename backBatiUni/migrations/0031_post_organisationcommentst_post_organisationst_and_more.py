# Generated by Django 4.0.2 on 2022-04-11 16:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backBatiUni', '0030_rename_stars_company_starspme_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='organisationCommentST',
            field=models.TextField(default='', verbose_name='Organisation Commentaire'),
        ),
        migrations.AddField(
            model_name='post',
            name='organisationST',
            field=models.IntegerField(default=0, verbose_name='Organisation'),
        ),
        migrations.AddField(
            model_name='post',
            name='securityCommentST',
            field=models.TextField(default='', verbose_name='Respect de la sécurité et de la propreté du chantier ST Commentaire'),
        ),
        migrations.AddField(
            model_name='post',
            name='securityST',
            field=models.IntegerField(default=0, verbose_name='Respect de la sécurité et de la propreté du chantier ST'),
        ),
        migrations.AddField(
            model_name='post',
            name='vibeCommentST',
            field=models.TextField(default='', verbose_name='Ambiance sur le chantier ST Commentaire'),
        ),
        migrations.AddField(
            model_name='post',
            name='vibeST',
            field=models.IntegerField(default=0, verbose_name='Ambiance sur le chantier ST'),
        ),
        migrations.AlterField(
            model_name='file',
            name='timestamp',
            field=models.FloatField(default=1649693587.569035, verbose_name='Timestamp de mise à jour'),
        ),
    ]