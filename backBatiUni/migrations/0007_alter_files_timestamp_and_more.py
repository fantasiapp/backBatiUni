# Generated by Django 4.0 on 2022-01-15 17:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('backBatiUni', '0006_rename_job_jobforcompany_job_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='files',
            name='timestamp',
            field=models.FloatField(default=1642266014.514213, verbose_name='Timestamp de mise à jour'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='userNameInternal',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.PROTECT, to='auth.user'),
        ),
    ]