# Generated by Django 4.0 on 2022-01-14 10:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backBatiUni', '0004_alter_files_ext_alter_files_name_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='files',
            old_name='company',
            new_name='Company',
        ),
        migrations.RenameField(
            model_name='jobforcompany',
            old_name='company',
            new_name='Company',
        ),
        migrations.RenameField(
            model_name='labelforcompany',
            old_name='company',
            new_name='Company',
        ),
        migrations.RenameField(
            model_name='userprofile',
            old_name='company',
            new_name='Company',
        ),
        migrations.AlterUniqueTogether(
            name='files',
            unique_together={('nature', 'name', 'Company')},
        ),
        migrations.AlterField(
            model_name='files',
            name='timestamp',
            field=models.FloatField(default=1642154548.849932, verbose_name='Timestamp de mise à jour'),
        ),
        migrations.AlterUniqueTogether(
            name='jobforcompany',
            unique_together={('job', 'Company')},
        ),
        migrations.AlterUniqueTogether(
            name='labelforcompany',
            unique_together={('label', 'Company')},
        ),
    ]