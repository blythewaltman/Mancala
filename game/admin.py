from django.contrib import admin

from .models import GameData, Question, Game, Board, Player

admin.site.register(Question)
admin.site.register(GameData)
admin.site.register(Game)
admin.site.register(Player)
