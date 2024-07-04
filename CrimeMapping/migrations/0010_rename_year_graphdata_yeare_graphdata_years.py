# Generated by Django 4.0.6 on 2022-08-15 10:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CrimeMapping', '0009_remove_graphdata_type_desc_remove_graphdata_block_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='graphdata',
            old_name='Year',
            new_name='YearE',
        ),
        migrations.AddField(
            model_name='graphdata',
            name='YearS',
            field=models.IntegerField(blank=True, choices=[(2001, 2001), (2002, 2002), (2003, 2003), (2005, 2005), (2006, 2006), (2007, 2007), (2008, 2008), (2009, 2009), (2010, 2010), (2011, 2011), (2012, 2012), (2013, 2013), (2014, 2014), (2015, 2015), (2016, 2016), (2017, 2017), (2018, 2018), (2019, 2019), (2020, 2020)], null=True),
        ),
    ]