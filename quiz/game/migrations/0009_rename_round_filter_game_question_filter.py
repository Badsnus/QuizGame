# Generated by Django 3.2.16 on 2022-12-23 16:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0008_game_round_filter'),
    ]

    operations = [
        migrations.RenameField(
            model_name='game',
            old_name='round_filter',
            new_name='question_filter',
        ),
    ]
