# Generated by Django 4.0.2 on 2022-07-07 08:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backBatiUni', '0007_alter_file_timestamp_alter_notification_timestamp_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recommandation',
            name='LastWorksiteDate',
        ),
        migrations.AddField(
            model_name='label',
            name='description',
            field=models.CharField(default='', max_length=2048, null=True, verbose_name='Description du métier'),
        ),
        migrations.AddField(
            model_name='label',
            name='fileName',
            field=models.CharField(default='Unkown', max_length=128, unique=True, verbose_name='Nom du fichier Associé'),
        ),
        migrations.AddField(
            model_name='label',
            name='site',
            field=models.CharField(default='', max_length=256, null=True, verbose_name='Site internet'),
        ),
        migrations.AddField(
            model_name='recommandation',
            name='lastWorksiteDate',
            field=models.DateField(blank=True, default=None, null=True, verbose_name='Date du dernier chantier'),
        ),
        migrations.AlterField(
            model_name='file',
            name='timestamp',
            field=models.FloatField(default=1657181132.97982, verbose_name='Timestamp de mise à jour'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='timestamp',
            field=models.FloatField(default=1657181132.977603, verbose_name='Timestamp de mise à jour'),
        ),
    ]
