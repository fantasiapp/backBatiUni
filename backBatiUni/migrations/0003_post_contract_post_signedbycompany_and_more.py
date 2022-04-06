# Generated by Django 4.0.2 on 2022-03-07 07:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backBatiUni', '0002_viewpost_userprofile_viewpost_postid_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='contract',
            field=models.IntegerField(default=None, null=True, verbose_name='Image du contrat'),
        ),
        migrations.AddField(
            model_name='post',
            name='signedByCompany',
            field=models.BooleanField(default=True, verbose_name='Signature de la PME'),
        ),
        migrations.AddField(
            model_name='post',
            name='signedBySubContractor',
            field=models.BooleanField(default=True, verbose_name='Signature du ST'),
        ),
        migrations.AlterField(
            model_name='file',
            name='timestamp',
            field=models.FloatField(default=1646638654.5464, verbose_name='Timestamp de mise à jour'),
        ),
    ]