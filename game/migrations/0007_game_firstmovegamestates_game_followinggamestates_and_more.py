# Generated by Django 4.1 on 2022-09-16 18:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0006_remove_player_iscomputer_game_issingleplayer'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='firstMoveGameStates',
            field=models.CharField(default='', max_length=200),
        ),
        migrations.AddField(
            model_name='game',
            name='followingGameStates',
            field=models.CharField(default='', max_length=200),
        ),
        migrations.AddField(
            model_name='game',
            name='originalPlayer',
            field=models.CharField(default='', max_length=200),
        ),
        migrations.AddField(
            model_name='game',
            name='originalSwaps',
            field=models.CharField(default='', max_length=200),
        ),
    ]
