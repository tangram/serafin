from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('codelogs', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='codelog',
            name='log',
            field=models.TextField(null=True, verbose_name='log', blank=True),
        ),
    ]
