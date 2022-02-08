# Generated by Django 4.0 on 2022-02-08 09:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backBatiUni', '0036_post_unitoftime_alter_files_timestamp'),
    ]

    operations = [
        migrations.RenameField(
            model_name='post',
            old_name='lattitude',
            new_name='latitude',
        ),
        migrations.RemoveField(
            model_name='post',
            name='Company',
        ),
        migrations.RemoveField(
            model_name='post',
            name='subContractor',
        ),
        migrations.AlterField(
            model_name='files',
            name='timestamp',
            field=models.FloatField(default=1644312746.455973, verbose_name='Timestamp de mise à jour'),
        ),
        migrations.CreateModel(
            name='Candidate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('isChoosen', models.BooleanField(default=False, verbose_name='Sous traitant selectionné')),
                ('company', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='Company', to='backBatiUni.company', verbose_name='Sous-Traitant')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]