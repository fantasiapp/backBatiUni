# Generated by Django 4.0 on 2022-01-10 09:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backBatiUni', '0009_alter_job_options_company_companyphone_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userprofile',
            old_name='userInternal',
            new_name='userNameInternal',
        ),
    ]
