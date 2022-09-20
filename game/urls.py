from django.urls import path
from . import views

#URLConf
urlpatterns = [
    path('welcome/', views.welcome, name="welcome"),
    path('singleplayer/', views.singlePlayer, name="single-player"),
    path('multiplayer/', views.multiPlayer, name="multi-player"),
    path('submit-multiplayer-names/', views.submitNames, name="submit-multiplayer-names"),
    path('submit-names/', views.submitNames, name="submit-names"),
    path('<int:game_id>/mancala/', views.mancala, name="mancala"),
    path('<int:game_id>/<int:row>/<int:col>/submit-human-move/', views.submitHumanMove, name="submit-human-move"),
    path('<int:game_id>/get-computer-move/', views.getComputerMove, name="get_computer_move")
]