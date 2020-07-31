# Generated by Django 3.0.5 on 2020-07-31 12:34

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plots', '0003_datecases'),
    ]

    operations = [
        migrations.CreateModel(
            name='Province',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('population', models.IntegerField(default=0)),
                ('cumulative_array', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), size=None)),
            ],
            options={
                'db_table': 'Italy_provinces',
                'abstract': False,
            },
        ),
        migrations.AlterModelTable(
            name='borough',
            table='London_boroughs',
        ),
    ]