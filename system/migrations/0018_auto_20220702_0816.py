# Generated by Django 2.2.28 on 2022-07-02 06:16

import collections
from django.db import migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0017_auto_20210311_0944'),
    ]

    operations = [
        migrations.AlterField(
            model_name='session',
            name='data',
            field=jsonfield.fields.JSONField(default={'edges': [], 'nodes': []}, load_kwargs={'object_pairs_hook': collections.OrderedDict}),
        ),
    ]