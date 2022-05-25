# Generated by Django 4.0.2 on 2022-05-25 15:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backBatiUni', '0055_post_creationdate_alter_file_timestamp_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='supervision',
            name='Mission',
        ),
        migrations.AddField(
            model_name='supervision',
            name='DatePost',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.PROTECT, to='backBatiUni.datepost', verbose_name='Tâche associée'),
        ),
        migrations.AlterField(
            model_name='file',
            name='timestamp',
            field=models.FloatField(default=1653493271.457978, verbose_name='Timestamp de mise à jour'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='timestamp',
            field=models.FloatField(default=1653493271.455907, verbose_name='Timestamp de mise à jour'),
        ),
        migrations.AlterField(
            model_name='post',
            name='boostTimestamp',
            field=models.FloatField(default=1653493271.454644, verbose_name='Timestamp de mise à jour'),
        ),
    ]
