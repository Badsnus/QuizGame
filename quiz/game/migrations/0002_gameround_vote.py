# Generated by Django 3.2.16 on 2022-12-14 09:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='gameround',
            name='vote',
            field=models.BooleanField(default=False),
        ),
    ]
