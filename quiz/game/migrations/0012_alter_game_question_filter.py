# Generated by Django 3.2.16 on 2022-12-23 16:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0011_alter_game_question_filter'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='question_filter',
            field=models.CharField(choices=[('?', 'Рандомный порядок'), ('pk', 'По порядку')], default='?', max_length=2, verbose_name='cортировка вопросов'),
        ),
    ]
