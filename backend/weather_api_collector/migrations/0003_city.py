# Generated by Django 5.0.1 on 2024-01-30 18:41

from django.db import migrations, models
from weather_api_collector.models import City
import csv


def load_cities(apps, schema_editor):
    file_path = 'data/worldcities.csv'

    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            population = float(row['population']) if row['population'] else 0
            City.objects.create(
                city=row['city'],
                city_ascii=row['city_ascii'],
                lat=float(row['lat']),
                lng=float(row['lng']),
                country=row['country'],
                iso2=row['iso2'],
                iso3=row['iso3'],
                admin_name=row['admin_name'],
                capital=row['capital'],
                population=population
            )


class Migration(migrations.Migration):

    dependencies = [
        ("weather_api_collector", "0002_alter_weatherdata_date"),
    ]

    operations = [
        migrations.CreateModel(
            name="City",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("city", models.CharField(max_length=255)),
                ("city_ascii", models.CharField(max_length=255)),
                ("lat", models.FloatField()),
                ("lng", models.FloatField()),
                ("country", models.CharField(max_length=255)),
                ("iso2", models.CharField(max_length=2)),
                ("iso3", models.CharField(max_length=3)),
                ("admin_name", models.CharField(max_length=255)),
                ("capital", models.CharField(max_length=255)),
                ("population", models.FloatField()),
            ],
        ),
        migrations.RunPython(load_cities),
    ]
