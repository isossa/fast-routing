# Generated by Django 3.0.10 on 2021-05-28 13:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cvrp', '0007_auto_20210528_0800'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='assigned',
            field=models.BooleanField(editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='location',
            name='language',
            field=models.ManyToManyField(help_text='Select a language', to='cvrp.Language'),
        ),
    ]
