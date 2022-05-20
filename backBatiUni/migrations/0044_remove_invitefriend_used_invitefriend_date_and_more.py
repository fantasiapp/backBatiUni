# Generated by Django 4.0.2 on 2022-05-01 19:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backBatiUni', '0043_datepost_deleted_datepost_validated_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='invitefriend',
            name='used',
        ),
        migrations.AddField(
            model_name='invitefriend',
            name='date',
            field=models.DateField(default=None, null=True, verbose_name="Date de l'inscription"),
        ),
        migrations.AddField(
            model_name='invitefriend',
            name='invitedUser',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='Invited', to='backBatiUni.userprofile'),
        ),
        migrations.AlterField(
            model_name='file',
            name='timestamp',
            field=models.FloatField(default=1651432276.679301, verbose_name='Timestamp de mise à jour'),
        ),
        migrations.AlterField(
            model_name='invitefriend',
            name='invitationAuthor',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='Author', to='backBatiUni.userprofile'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='timestamp',
            field=models.FloatField(default=1651432276.677139, verbose_name='Timestamp de mise à jour'),
        ),
    ]