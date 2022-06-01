# Generated by Django 4.0.2 on 2022-05-29 13:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backBatiUni', '0057_supervision_mission_alter_file_timestamp_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='detailedpost',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='detailedpost',
            name='DatePost',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='DateOfDetail', to='backBatiUni.datepost', verbose_name='Date associée'),
        ),
        migrations.AlterField(
            model_name='file',
            name='timestamp',
            field=models.FloatField(default=1653832056.788125, verbose_name='Timestamp de mise à jour'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='timestamp',
            field=models.FloatField(default=1653832056.78593, verbose_name='Timestamp de mise à jour'),
        ),
        migrations.AlterField(
            model_name='post',
            name='boostTimestamp',
            field=models.FloatField(default=1653832056.784646, verbose_name='Timestamp de mise à jour'),
        ),
        migrations.AlterUniqueTogether(
            name='detailedpost',
            unique_together={('Post', 'Mission', 'DatePost')},
        ),
        migrations.RemoveField(
            model_name='detailedpost',
            name='date',
        ),
    ]