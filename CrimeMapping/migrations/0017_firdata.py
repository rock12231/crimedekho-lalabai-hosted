# Generated by Django 4.0.6 on 2023-12-27 07:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CrimeMapping', '0016_authenticate_alter_graphdata_where'),
    ]

    operations = [
        migrations.CreateModel(
            name='FirData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('case_no', models.TextField(null=True)),
                ('date', models.TextField(null=True)),
                ('ipc', models.TextField(null=True)),
                ('time', models.TextField(null=True)),
                ('CrPC', models.TextField(null=True)),
                ('date_happened', models.TextField(null=True)),
                ('date_reported', models.TextField(null=True)),
                ('format_fir_type', models.TextField(null=True)),
                ('address', models.TextField(null=True)),
                ('distance_police_station', models.TextField(null=True)),
                ('name', models.TextField(null=True)),
                ('father_name', models.TextField(null=True)),
                ('age', models.TextField(null=True)),
                ('nationality', models.TextField(null=True)),
                ('office_Address', models.TextField(null=True)),
                ('additional_info', models.TextField(null=True)),
                ('suspected_individual', models.TextField(null=True)),
                ('location', models.TextField(null=True)),
                ('file', models.URLField()),
            ],
        ),
    ]
