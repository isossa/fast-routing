# Generated by Django 3.0.10 on 2021-05-28 13:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cvrp', '0006_auto_20210528_0738'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='language',
            field=models.ManyToManyField(help_text='Select a language', null=True, to='cvrp.Language'),
        ),
    ]
