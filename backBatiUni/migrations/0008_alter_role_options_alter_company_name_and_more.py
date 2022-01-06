# Generated by Django 4.0 on 2022-01-05 19:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('backBatiUni', '0007_alter_job_options_alter_role_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='role',
            options={},
        ),
        migrations.AlterField(
            model_name='company',
            name='name',
            field=models.CharField(max_length=128, unique=True, verbose_name='Nom de la société'),
        ),
        migrations.AlterField(
            model_name='company',
            name='siret',
            field=models.CharField(default=None, max_length=32, null=True, unique=True, verbose_name='Numéro de Siret'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='userInternal',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='auth.user'),
        ),
    ]
