# Generated by Django 3.2.5 on 2021-07-20 12:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anomaly', '0010_runstatus_logs'),
    ]

    operations = [
        migrations.CreateModel(
            name='Settings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(blank=True, null=True)),
                ('value', models.TextField(blank=True, null=True)),
            ],
        ),
    ]