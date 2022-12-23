# Generated by Django 3.2.16 on 2022-12-23 16:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0015_alter_game_question_filter'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='question_filter',
            field=models.CharField(choices=[('?', 'Рандомный порядок'), ('pk', 'По порядку в таблице')], default='?', max_length=2, verbose_name='cортировка вопросов'),
        ),
    ]
