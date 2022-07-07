# Generated by Django 4.0.2 on 2022-07-07 10:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backBatiUni', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='timestamp',
            field=models.FloatField(default=1657190201.226684, verbose_name='Timestamp de mise à jour'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='timestamp',
            field=models.FloatField(default=1657190201.224476, verbose_name='Timestamp de mise à jour'),
        ),
        migrations.CreateModel(
            name='Recommandation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('firstNameRecommanding', models.CharField(blank=True, default='', max_length=128, verbose_name='first name of recommander')),
                ('lastNameRecommanding', models.CharField(blank=True, default='', max_length=128, verbose_name='last name of recommander')),
                ('companyNameRecommanding', models.CharField(blank=True, default='', max_length=128, verbose_name='company name of recommander')),
                ('qualityStars', models.IntegerField(default=0.0, verbose_name="Notation sous forme d'étoile")),
                ('qualityComment', models.CharField(blank=True, default='', max_length=3000, verbose_name='company name of recommander')),
                ('securityStars', models.IntegerField(default=0.0, verbose_name="Notation sous forme d'étoile")),
                ('securityComment', models.CharField(blank=True, default='', max_length=3000, verbose_name='company name of recommander')),
                ('organisationStars', models.IntegerField(default=0.0, verbose_name="Notation sous forme d'étoile")),
                ('organisationComment', models.CharField(blank=True, default='', max_length=3000, verbose_name='company name of recommander')),
                ('lastWorksiteDate', models.DateField(blank=True, default=None, null=True, verbose_name='Date du dernier chantier')),
                ('date', models.DateField(default=None, null=True, verbose_name="Date de l'inscription")),
                ('companyRecommanded', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='recommanded', to='backBatiUni.company', verbose_name='Company who is recommanded')),
                ('view', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='viewRecommandation', to='backBatiUni.role', verbose_name='Rôle Sélectionné')),
            ],
            options={
                'verbose_name': 'Recommandation',
            },
        ),
    ]