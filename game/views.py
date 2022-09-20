from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from game.models import Game
from game.models import Player
from game.models import Board
from game.getAIMove import getAIMove

def welcome(request):
    return render(request, 'welcome.html')

def singlePlayer(request):
    return render(request, 'single_player.html')

def multiPlayer(request):
    return render(request, 'multi_player.html')

def submitNames(request):
    player_one_name = request.POST['player_one_name']
    try:
        player_two_name = request.POST['player_two_name']
        is_single_player = False
    except:
        player_two_name = 'Computer'
        is_single_player = True
    game = Game(isSinglePlayer=is_single_player)
    game.save()
    game.player_set.create(name = player_one_name)
    game.player_set.create(name = player_two_name)
    board = Board(game = game)
    board.setInitialState()
    board.save()
    return HttpResponseRedirect(reverse('mancala', args = (game.id,)))

def mancala(request, game_id):
    game = Game.objects.get(pk=game_id)
    board_state = game.board.getState()
    # Check that the game isn't over
    if(game.checkGameOver(board_state) == False):
        players = Player.objects.filter(game__pk = game.id)
        valid_moves = game.getValidMoveSelection(board_state)
        board_data = game.getValidMoveAndValue(board_state, valid_moves)
        if (game.turn == 1 and game.isSinglePlayer == True):
            is_computers_turn = 0
        else:
            is_computers_turn = 1
        data = {
            'player_name' : players[game.turn].name,
            'game_id': game_id,
            'board_data' : board_data,
            'pits' : [board_data[0][1:6:1]] + [board_data[1][0:5:1]],
            'is_computers_turn': is_computers_turn,
            'repeat_turn': game.repeatTurn,
            'is_single_player': game.isSinglePlayer,
        }
        return render(request, 'mancala.html', {'data':data})
    else:
        game.isOver = True
        game.save()
        return gameOver(request, game_id)
    
def submitHumanMove(request, game_id, row, col):
    game = Game.objects.get(pk=game_id)
    board_state = game.board.getState()
    if game.turn == 1: col -= 1
    board_result = game.makeMove(row, col, board_state)
    game.board.setState(board_result)
    if(game.repeatTurn == False):
        game.swapTurn()
    game.save()
    game.board.save()
    return HttpResponseRedirect(reverse('mancala', args = (game.id,)))

def getComputerMove(request, game_id):
    game = Game.objects.get(pk=game_id)
    board_state = game.board.getState()
    valid_moves = game.getValidMoveSelection(board_state)
    move = getAIMove(game, valid_moves)
    board_result = game.makeMove(move[0], move[1], board_state)
    game.board.setState(board_result)
    if(game.repeatTurn == False):
        game.swapTurn()
    game.save()
    game.board.save()
    return HttpResponseRedirect(reverse('mancala', args=(game.id,)))

def gameOver(request, game_id):
    game = Game.objects.get(pk = game_id)
    players = Player.objects.filter(game__pk = game.id)
    final_board_state = game.board.getFinalState()
    final_board_data = game.getValidMoveAndValue(final_board_state, [])
    winner = game.determineWinner(final_board_state)
    if(winner < 2):
        winner_name = players[winner].name
    else:
        winner_name = "Tie"
    data = {
            'winner' : winner,
            'winner_name': winner_name,
            'player_0_mancala_val': final_board_data[0][0]['val'],
            'player_0_mancala_image' : final_board_data[0][0]['image'],
            'player_1_mancala_val': final_board_data[1][5]['val'],
            'player_1_mancala_image' : final_board_data[1][5]['image'],
            'final_board_data ': final_board_data,
            'pits' : [final_board_data[0][1:6:1]] + [final_board_data[1][0:5:1]],
        }
    return render(request, 'game_over.html', {'data':data})

