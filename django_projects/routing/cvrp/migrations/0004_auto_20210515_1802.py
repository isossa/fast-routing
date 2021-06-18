# Generated by Django 3.2.3 on 2021-05-15 23:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cvrp', '0003_auto_20210515_1736'),
    ]

    operations = [
        migrations.CreateModel(
            name='Driver',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=200)),
                ('last_name', models.CharField(max_length=200)),
                ('role', models.CharField(choices=[('PERMANENT', 'Permanent'), ('VOLUNTEER', 'Volunteer'), ('NONE', 'None')], default='None', max_length=20)),
                ('created_on', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('availability_score', models.PositiveIntegerField(editable=False)),
            ],
            options={
                'verbose_name': 'Driver',
                'verbose_name_plural': 'Drivers',
            },
        ),
        migrations.AlterModelOptions(
            name='route',
            options={'verbose_name': 'Route', 'verbose_name_plural': 'Routes'},
        ),
        migrations.AddField(
            model_name='location',
            name='created_on',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='location',
            name='last_modified',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='route',
            name='created_on',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='route',
            name='last_modified',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='route',
            name='assigned_to',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='cvrp.driver'),
        ),
    ]