import math
import copy

# List containing the game states after the computer makes each initial move
firstMoveGameStates = []
# List containing the game states that follow each inital move
followingGameStates = []
# List containing who made the inital move in the current move sequence
originalPlayer = []
# List containing the number of swaps that have been completed at the start of the move sequence
originalSwaps = []

def getAIMove(game, valid_moves):
    print("Getting the computers move...")
    if(len(valid_moves) == 1):
        move = valid_moves[0]
    else:
        move = getBestMove(game, 1 , False, valid_moves)
    print("Game making move: ", move)
    return move

def getBestMove(game, depth, isPlayer0, possible_moves):
    bestMove = None
    alpha = -math.inf
    beta = math.inf
    score = -math.inf
    for move in list(reversed(possible_moves)): #reverse moves to try position closest to the player's mancala first
        originalPlayer.append(game.turn)
        firstMoveGameStates.append(copy.deepcopy(game.board.getState()))
        game.board.setState(game.makeMove(move[0], move[1], game.board.getState()))
        if(game.checkGameOver(game.board.getState()) == True):
            endState = game.board.getState()
            if(isPlayer0):
                newScore = sum(endState[0]) - sum(endState[1])
            else:
                newScore = sum(endState[1]) - sum(endState[0])
        else:
            if (game.repeatTurn == False):
                game.swapTurn()
                newScore = minimax(False, game, 1, depth, isPlayer0, alpha, beta)
            else:
                newScore = minimax(True, game, 0, depth, isPlayer0, alpha, beta)
        game.turn = originalPlayer.pop()
        game.board.setState(firstMoveGameStates.pop())
        if(newScore > score):
            score = newScore
            bestMove = move
        alpha = max(score, alpha)
    return bestMove

def minimax(isMaxTurn, game, numTurnSwapsDone, depth, isPlayer0, alpha, beta):
    state = game.board.getState()

    if((numTurnSwapsDone >= depth and game.repeatTurn == False) or (game.checkGameOver(game.board.getState()) == True)):
        if(isPlayer0):
            return (state[0][0] - state[1][5])
        else:
            return (state[1][5] - state[0][0])

    if(isMaxTurn):
        score = -math.inf
    else:
        score = math.inf

    scores = []
    print("state: ", state)
    print("alpha: %f, beta: %f" % (alpha, beta))

    for move in list(reversed(game.getValidMoveSelection(state))):
        originalPlayer.append(game.turn)
        originalSwaps.append(numTurnSwapsDone)
        followingGameStates.append(copy.deepcopy(game.board.getState()))
        game.board.setState(game.makeMove(move[0], move[1], state))
        if (game.repeatTurn == False):
            game.swapTurn()
            numTurnSwapsDone += 1
            score = minimax(not isMaxTurn, game, numTurnSwapsDone, depth, isPlayer0, alpha, beta)
            scores.append(score)
        else:
            score = minimax(isMaxTurn, game, numTurnSwapsDone, depth, isPlayer0, alpha, beta)
            scores.append(score)
        if(isMaxTurn):
            if (score >= beta):
                followingGameStates.pop()
                originalPlayer.pop()
                originalSwaps.pop()
                return max(scores) if isMaxTurn else min(scores)
            alpha = max(alpha, score)
        else:
            if(score <= alpha):
                followingGameStates.pop()
                originalPlayer.pop()
                originalSwaps.pop()
                return max(scores) if isMaxTurn else min(scores)
            beta = min(beta, score)  
        game.turn = originalPlayer.pop()
        game.board.setState(followingGameStates.pop())
        numTurnSwapsDone = originalSwaps.pop()
    return max(scores) if isMaxTurn else min(scores)