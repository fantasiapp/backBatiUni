# Generated by Django 4.0 on 2022-01-05 15:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backBatiUni', '0005_alter_company_siret'),
    ]

    operations = [
        migrations.CreateModel(
            name='Label',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default=False, max_length=128, unique=True, verbose_name='Nom du label')),
            ],
        ),
        migrations.AddField(
            model_name='company',
            name='capital',
            field=models.IntegerField(default=None, null=True, verbose_name="Capital de l'entreprise"),
        ),
        migrations.AddField(
            model_name='company',
            name='logo',
            field=models.CharField(default=None, max_length=256, null=True, verbose_name="Path du logo de l'entreprise"),
        ),
        migrations.AddField(
            model_name='company',
            name='stars',
            field=models.IntegerField(default=None, null=True, verbose_name="Notation sous forme d'étoile"),
        ),
        migrations.AddField(
            model_name='company',
            name='webSite',
            field=models.CharField(default=None, max_length=256, null=True, verbose_name='Url du site Web'),
        ),
        migrations.AddField(
            model_name='company',
            name='labels',
            field=models.ManyToManyField(to='backBatiUni.Label'),
        ),
    ]