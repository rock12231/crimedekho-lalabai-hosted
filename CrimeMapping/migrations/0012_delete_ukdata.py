# Generated by Django 4.0.5 on 2022-09-05 03:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('CrimeMapping', '0011_ukdata_alter_graphdata_type_alter_graphdata_yeare_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ukdata',
        ),
    ]