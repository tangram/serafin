# Generated by Django 2.2 on 2020-08-25 15:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_auto_20200421_2213'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='secondary_phone',
            field=models.CharField(max_length=32, null=True, verbose_name='secondary phone number'),
        ),
    ]