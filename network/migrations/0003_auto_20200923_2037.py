# Generated by Django 3.1.1 on 2020-09-23 19:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0002_auto_20200922_2139'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='edited',
            field=models.BooleanField(default=False),
        ),
    ]
