# Generated by Django 3.2.5 on 2022-02-24 09:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dataset', '0001_initial'),
        ('cueSearch', '0005_searchcardtemplate_connectiontype'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='searchcardtemplate',
            name='connectionType',
        ),
        migrations.AddField(
            model_name='searchcardtemplate',
            name='connectionType',
            field=models.ManyToManyField(blank=True, null=True, to='dataset.ConnectionType'),
        ),
    ]
