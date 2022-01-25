# Generated by Django 3.2.5 on 2022-01-12 11:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cueSearch", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="SearchCardTemplate",
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
                ("templateName", models.TextField(blank=True, null=True)),
                ("title", models.TextField(blank=True, null=True)),
                ("bodyText", models.TextField(blank=True, null=True)),
                ("sql", models.TextField(blank=True, null=True)),
                ("supportedVariables", models.TextField(blank=True, null=True)),
            ],
        ),
    ]
