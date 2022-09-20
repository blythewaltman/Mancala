import datetime
import json

from django.db import models
from django.utils import timezone

# Create your models here.
class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    def __str__(self):
        return self.question_text
    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default = 0)
    def __str__(self):
        return self.choice_text

class GameData(models.Model):
    player_one_name = models.CharField(max_length=200)
    player_two_name = models.CharField(max_length=200)
    def __str__(self):
        game_id = str(self.id)
        return game_id

class Game(models.Model):
    isOver = models.BooleanField(default = False)
    winner = models.IntegerField(default = 0)
    turn = models.IntegerField(default = 0)
    repeatTurn = models.BooleanField(default = False)
    isSinglePlayer = models.BooleanField(default = False)

    #Variables for tracking AI Algorithm states
    firstMoveGameStates = models.CharField(max_length=200, default = "")
    followingGameStates = models.CharField(max_length=200, default = "")
    originalPlayer = models.CharField(max_length=200, default = "")
    originalSwaps = models.CharField(max_length=200, default = "")

    def popAIState(self, field):
        match field:
            case "firstMoveGameStates":
                firstMoveGameStates = json.loads(self.firstMoveGameStates)
                val = firstMoveGameStates.pop()
                self.firstMoveGameStates = json.dumps(firstMoveGameStates)
                return val
            case "followingGameStates":
                followingGameStates = json.loads(self.followingGameStates)
                val = followingGameStates.pop()
                self.followingGameStates = json.dumps(followingGameStates)
                return val
            case "originalPlayer":
                originalPlayer = json.loads(self.originalPlayer)
                val = originalPlayer.pop()
                self.originalPlayer = json.dumps(originalPlayer)
                return val
            case "originalSwaps":
                originalSwaps = json.loads(self.originalSwaps)
                val = originalSwaps.pop()
                self.originalSwaps = json.dumps(originalSwaps)
                return val
            case _:
                return None

    def appendAIState(self, field, val):
        match field:
            case "firstMoveGameStates":
                firstMoveGameStates = json.loads(self.firstMoveGameStates)
                firstMoveGameStates.append(val)
                self.firstMoveGameStates = json.dumps(firstMoveGameStates)
            case "followingGameStates":
                followingGameStates = json.loads(self.followingGameStates)
                followingGameStates.append(val)
                self.followingGameStates = json.dumps(followingGameStates)
            case "originalPlayer":
                originalPlayer = json.loads(self.originalPlayer)
                originalPlayer.append(val)
                self.originalPlayer = json.dumps(originalPlayer)
            case "originalSwaps":
                originalSwaps = json.loads(self.originalSwaps)
                originalSwaps.append(val)
                self.originalSwaps = json.dumps(originalSwaps)
            case _:
                return None       

    def makeMove(self, startingRow, startingCol, arr):
        row = startingRow
        col = startingCol
        player = self.turn
        numStones = arr[row][col]
        arr[row][col] = 0
        while (numStones > 0):
            # if we are in row 0 index to the left
            if (row == 0):
                col -= 1
            # if we are in row 1 index to the right
            elif (row == 1):
                col += 1
            # if we have indexed too far left switch down to row 1 and reset col to 0
            if (col == -1):
                row = 1
                col = 0
            # if we have indexed too far right switch up to row 0 and reset col to 5
            elif (col == 6):
                row = 0
                col = 5
            if (((player == 1 and row == 0 and col == 0) or (player == 0 and row == 1 and col == 5)) is not True):
                arr[row][col] += 1
                numStones -= 1
        arr = self.determineSpecialRules(row, col, arr)
        return arr

    def swapTurn(self):
        self.turn = 1 - self.turn

    def determineSpecialRules(self, row, col, arr):
        self.repeatTurn = False
        if (self.turn == 0):
            if (row == 0 and col == 0):
                self.repeatTurn = True
            elif (row == 0 and arr[row][col] == 1):
                if(arr[1][col-1] > 0):
                    arr[0][0] += arr[1][col-1]
                    arr[1][col-1] = 0
                    arr[0][0] += arr[row][col]
                    arr[row][col] = 0
        elif (self.turn == 1):
            if (row == 1 and col == 5):
                self.repeatTurn = True
            elif (row == 1 and arr[row][col] == 1):
                if(arr[0][col+1] > 0):
                    arr[1][5] += arr[0][col+1]
                    arr[0][col + 1] = 0
                    arr[1][5] += arr[row][col]
                    arr[row][col] = 0
        return arr

    def getValidMoveSelection(self, boardState):
        possibleIndexs = []
        if (self.turn == 0):
            possiblePits = boardState[0][1:6:1]
            for idx, pit in enumerate(possiblePits):
                if pit > 0:
                    possibleIndexs.append([0, idx+1])
        else:
            possiblePits = boardState[1][0:5:1]
            for idx, pit in enumerate(possiblePits):
                if pit > 0:
                    possibleIndexs.append([1, idx])
        return possibleIndexs

    def getValidMoveAndValue(self, board, validMoves):
        arr = []
        valImage = 0
        for idx, row in enumerate(board):
            newRow = []
            for idy, col in enumerate(row):
                if(board[idx][idy] >= 10):
                    valImage = 10
                else:
                    valImage = board[idx][idy]
                if((idx == 0 and idy == 0) or (idx == 1 and idy == 5)):
                    imageUrl = "mancala" + str(valImage) + ".png"
                else:
                    imageUrl = "pit" + str(valImage) + ".png"
                if([idx,idy] in validMoves):
                    newRow.append({"val" : board[idx][idy], "valid": True, "image":imageUrl})
                else:
                    newRow.append({"val": board[idx][idy], "valid": False, "image":imageUrl})
            arr.append(newRow)
        return arr

    def checkGameOver(self, boardState):
        player0PitTotal = sum(boardState[0][1:6:1])
        player1PitTotal = sum(boardState[1][0:5:1])
        if (player0PitTotal == 0 or player1PitTotal == 0):
            return True
        else:
            return False

    def determineWinner(self, boardState):
        player0Total = boardState[0][0]
        player1Total = boardState[1][5]

        if (player0Total > player1Total):
            return 0 # player 0 won
        elif(player0Total < player1Total):
            return 1 # player 1 won
        else:
            return 2 # the game was a tie


class Player(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, default="Computer")

class Board(models.Model):
    game = models.OneToOneField(
        Game,
        on_delete=models.CASCADE,
        primary_key=True
    )
    set = models.BooleanField(default=False)
    row1 = models.CharField(max_length=200, default = "")
    row2 = models.CharField(max_length=200, default = "")

    def getState(self):
       row_one = json.loads(self.row1)
       row_two = json.loads(self.row2)
       state = [row_one, row_two]
       return state

    def setInitialState(self):
        self.row1 = json.dumps([0,4,4,4,4,4])
        self.row2 = json.dumps([4,4,4,4,4,0])

    def setState(self, board):
        self.row1 = json.dumps(board[0])
        self.row2 = json.dumps(board[1])

    def getFinalState(self):
        # When one player no longer has any seeds in any of their pits, the game ends.
        # The other player moves all remaining seeds to their mancala
        row_one = json.loads(self.row1)
        row_two = json.loads(self.row2)
        row_one[0] = sum(row_one)
        row_two[1] = sum(row_two)
        row_one = [row_one[0], 0, 0, 0, 0, 0]
        row_two = [0, 0, 0, 0, 0, row_two[5]]
        self.row1 = json.dumps(row_one)
        self.row2 = json.dumps(row_two)
        return [row_one, row_two]