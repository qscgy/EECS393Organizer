# Generated by Django 3.0.4 on 2020-03-16 00:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cal', '0003_auto_20200316_0000'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='end_date',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='end_hm',
            field=models.TimeField(null=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='end_time',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='start_hm',
            field=models.TimeField(null=True),
        ),
    ]
