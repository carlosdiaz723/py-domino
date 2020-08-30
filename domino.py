from pprint import pprint as pretty
import matplotlib.pyplot as plt
import numpy as np
import random


class Piece:
    '''
    ATTRIBUTES      TYPE
    value1          int
    value2          int
    sum             int
    isDouble        bool


    METHODS
    equalTo()       bool
    '''

    def __init__(self, values: tuple):
        assert values[0] in range(7) and values[1] in range(7)
        self.values = values
        self.value1 = values[0]
        self.value2 = values[1]
        self.sum = self.value1 + self.value2
        self.isDouble = self.value1 == self.value2

    def equalTo(self, other):
        match = self.value1 == other.value1 and self.value2 == other.value2
        opp = self.value1 == other.value2 and self.value2 == other.value1
        return match or opp


class Player:
    '''
    A Player has a name, hand of pieces, strategies,
    and keeps track of their own score and wins.

    ATTRIBUTES          TYPE
    hand                list(Pieces)
    name                str
    strategy            str
    startingStrategy    str
    score               int
    wins                int
    capicuaWins         int
    cumulativeWins      list(int)
    cumulativeScores    list(int)

    METHODS
    addPiece(Piece)     bool (success flag)
    removePiece(Piece)  bool (success flag)
    '''

    def __init__(self, name: str, strategy='random',
                 startingStrategy='random'):
        self.hand = list()
        self.name = name
        self.strategy = strategy
        self.startingStrategy = startingStrategy
        self.score, self.wins, self.capicuaWins = 0, 0, 0
        self.cumulativeWins, self.cumulativeScores = list(), list()

    def addPiece(self, myPiece: Piece):
        '''
        Adds a given piece to the player's hand

        Returns if add was successful
        '''
        if len(self.hand) not in range(7):
            return False
        self.hand.append(myPiece)
        return True

    def removePiece(self, myPiece):
        '''
        Removes a given piece from the player

        Returns whether or not it was present (True, False)
        '''
        for piece in self.hand:
            if piece.equalTo(myPiece):
                self.hand.remove(myPiece)
                return True
        return False


class Game:
    '''
    A Game has players and a table and simulates gameplay.

    ATTRIBUTES          TYPE                DESCRIPTION
    currentAvailable    list(Pieces)        the pieces available to be
                                                picked up by players

    table               list(Pieces)        the pieces that have been played

    closes              int                 the number of games that have ended
                                                closed (game is decided by
                                                lowest count)

    capicuaWin          bool                True if most recent win was capicua

    players             list(Players)       players in the game in turn order
    end1, end2          int, int            the current ends of the table
    '''

    def __init__(self, players: list):
        self.currentAvailable = allPieces[:]
        self.table, self.end1, self.end2 = list(), int(), int()
        self.closes = 0
        self.capicuaWin = False
        self.players = players

    def reset(self):
        '''
        clear hands and table for a new game
        '''
        for player in self.players:
            player.hand.clear()
        self.table.clear()
        self.capicuaWin = False
        self.end1, self.end2 = int(), int()
        self.currentAvailable = allPieces[:]

    def shuffle(self):
        '''
        randomly assign pieces to each player
        '''
        for _ in range(7):
            for player in self.players:
                randomPick = random.choice(self.currentAvailable)
                self.currentAvailable.remove(randomPick)
                player.addPiece(randomPick)

    def printPieces(self, pieces: list()):
        for piece in pieces:
            print('({}, {}), '.format(piece.value1, piece.value2), end='')
        print()

    def printStatus(self):
        '''
        prints player names and current hands
        '''
        for player in self.players:
            print(player.name)
            for piece in player.hand:
                print(piece.values, end='')
            print('\n')

    def isCapicua(self, piece: Piece):
        '''
        True if given piece can be played on both current ends;
        False otherwise
        '''
        return piece.equalTo(Piece((self.end1, self.end2)))

    def possiblePlays(self, player: Player):
        '''
        Returns a list of possible pieces the player can play currently
        (as a list of tuples: (Piece, endNumber))
        '''
        possible = list()
        for piece in player.hand:
            if self.end1 in piece.values:
                possible.append((piece, '1'))
            if self.end2 in piece.values:
                possible.append((piece, '2'))
        return possible

    def doubleOrLargest(self, player: Player):
        '''
        implementation of 'double or largest' opening strategy

        Player will select a piece that is
        1) The largest double in their hand, or if Player has no doubles,
        2) has the largest sum in their hand
        '''
        doubles = list()
        for piece in player.hand:
            if piece.isDouble:
                doubles.append(piece)
        if len(doubles) > 0:
            largestDouble = doubles[0]
            for piece in doubles:
                if piece.value1 > largestDouble.value1:
                    largestDouble = piece
            return largestDouble
        else:
            # no doubles, play largest sum
            largestPiece = player.hand[0]
            for piece in player.hand:
                if piece.sum > largestPiece.sum:
                    largestPiece = piece
            return largestPiece

    def count(self, player: Player):
        '''
        returns a total count of the Player's hand
        '''
        total = 0
        for piece in player.hand:
            total += piece.sum
        return total

    def win(self, player: Player, capicua=False):
        '''
        returns a tuple of (Player, int) which corresponds to
        the winning player and their score
        '''
        score = 0
        for otherPlayer in self.players:
            if otherPlayer is not player:
                score += self.count(otherPlayer)
        if capicua:
            self.capicuaWin = True
            score *= 2
        return player, score

    def printTable(self):
        '''
        prints pieces currently on table and attempts to orient
        them so that adjacent pieces correctly fit with each other
        '''
        if len(self.table) == 0:
            return "Empty"

        master = str(self.table[0].values) + ' '
        if len(self.table) == 1:
            print(master)
            return

        for piece in self.table[1:]:
            if piece.value1 == int(master[-3]):
                master += str(piece.values) + ' '
            else:
                master += '({}, {}) '.format(piece.value2, piece.value1)
        print(master)

    def closed(self):
        '''
        closed() is an indirect call to win(Player)
        closed() determines the winner as the player with the lowest count
        score is calculated as usual (sum of other player's counts)
        '''
        self.closes += 1
        lowest = 1000
        lowestPlayer = self.players[0]
        for player in self.players:
            if self.count(player) < lowest:
                lowest = self.count(player)
                lowestPlayer = player
        return self.win(lowestPlayer)

    def start(self, trace=False):
        '''
        starts and runs the game
        optional trace bool allows for printing info as the game progresses
        '''
        passes = int()
        for _ in range(25):
            passes = 0
            for player in self.players:
                # first move exception
                if len(self.table) == 0:
                    piece = Piece((0, 0))
                    if player.startingStrategy == 'random':
                        piece = random.choice(player.hand)
                    elif player.startingStrategy == 'doubleOrLargest':
                        piece = self.doubleOrLargest(player)
                    self.end1, self.end2 = piece.values
                    self.table.append(piece)
                    player.removePiece(piece)
                    if trace:
                        print('Player: {} plays {}'.format(
                            player.name, str(piece.values)))
                        self.printTable()
                    continue

                possible = self.possiblePlays(player)
                if len(possible) == 0:
                    passes += 1
                    if passes == 4:
                        break
                    if trace:
                        print('Player: {} passes'.format(player.name))
                    continue

                # strategy switch
                if player.strategy == 'random':
                    piece, end = random.choice(possible)

                player.removePiece(piece)
                if trace:
                    print('Player: {} plays {}'.format(
                        player.name, str(piece.values)))

                # check win
                if len(player.hand) == 0:
                    return self.win(player, capicua=self.isCapicua(piece))

                # set new ends
                if end == '1':
                    if piece.value1 == self.end1:
                        self.end1 = piece.value2
                    else:
                        self.end1 = piece.value1
                    self.table.insert(0, piece)
                else:
                    if piece.value1 == self.end2:
                        self.end2 = piece.value2
                    else:
                        self.end2 = piece.value1
                    self.table.append(piece)
                if trace:
                    self.printTable()
            if passes == 4:
                break
        if passes == 4:
            return self.closed()


class GameMaster:
    '''
    handles multiple games and keeps track of stats
    '''

    def __init__(self, playerNames: list, strategies: list,
                 startingStrategies: list, maxGames=1, maxScore=None,
                 maxWins=None, startingPlayer='random'):
        self.playerNames = playerNames
        self.strategies = strategies
        self.startingStrategies = startingStrategies
        self.players = list()
        for index, name in enumerate(playerNames):
            self.players.append(
                Player(name, strategies[index], startingStrategies[index]))
        self.maxGames = maxGames
        self.startingPlayer = startingPlayer
        self.gamesPlayed = 0
        self.game = Game(self.players)
        self.maxScore = maxScore
        self.maxWins = maxWins

    def finish(self):
        master = dict()
        players = dict()
        for player in self.players:
            playerstats = dict()
            playerstats['strategy'] = player.strategy
            playerstats['starting_strategy'] = player.startingStrategy
            playerstats['wins'] = player.wins
            playerstats['wins_per_game'] = round(
                player.wins/self.gamesPlayed, 3)
            playerstats['capicuas'] = player.capicuaWins
            try:
                playerstats['capicuas_per_win'] = round(
                    player.capicuaWins/player.wins, 3)
            except ZeroDivisionError:
                playerstats['capicuas_per_win'] = 0
            playerstats['score'] = player.score
            players[player.name] = playerstats
        master['players'] = players
        master['closes'] = self.game.closes
        master['closes_per_game'] = self.game.closes/self.gamesPlayed
        master['max_games'] = self.maxGames
        master['games_played'] = self.gamesPlayed
        master['max_wins'] = self.maxWins
        master['max_score'] = self.maxScore
        return master

    def run(self, trace=False):
        for _ in range(self.maxGames):
            self.game.reset()
            self.game.shuffle()
            winner, score = self.game.start(trace)
            if trace:
                print('Player: {} WINS'.format(winner.name))
            winner.wins += 1
            for player in self.game.players:
                player.cumulativeWins.append(player.wins)
            if self.game.capicuaWin:
                winner.capicuaWins += 1
            winner.score += score
            for player in self.game.players:
                player.cumulativeScores.append(player.score)
            self.gamesPlayed += 1
            if self.maxWins is not None:
                if winner.wins >= self.maxWins:
                    return self.finish()
            if self.maxScore is not None:
                if winner.score >= self.maxScore:
                    return self.finish()
            if self.startingPlayer == 'random':
                random.shuffle(self.game.players)
            elif self.startingPlayer == 'winner':
                index = self.game.players.index(winner)
                self.game.players = self.game.players[index:] + \
                    self.game.players[:index]

        return self.finish()

    def plotHelp(self):
        x = np.arange(1, self.gamesPlayed + 1)
        _, ax = plt.subplots(2)
        winsList, scoresList = list(), list()
        for player in self.game.players:
            winsList.append(np.array(player.cumulativeWins))
            scoresList.append(np.array(player.cumulativeScores))
        for index in range(4):
            ax[0].plot(x, winsList[index], label=self.game.players[index].name)
            ax[1].plot(x, scoresList[index],
                       label=self.game.players[index].name)
        ax.flat[0].set(xlabel='Games Played', ylabel='Wins')
        ax.flat[1].set(xlabel='Games Played', ylabel='Scores')
        plt.legend(loc='upper left')
        plt.show()


tuples = [(6, 6),
          (6, 5), (5, 5),
          (6, 4), (5, 4), (4, 4),
          (6, 3), (5, 3), (4, 3), (3, 3),
          (6, 2), (5, 2), (4, 2), (3, 2), (2, 2),
          (6, 1), (5, 1), (4, 1), (3, 1), (2, 1), (1, 1),
          (6, 0), (5, 0), (4, 0), (3, 0), (2, 0), (1, 0), (0, 0)
          ]
allPieces = list()
for t in tuples:
    allPieces.append(Piece(t))

r = 'random'
dol = 'doubleOrLargest'
allRandom = [r, r, r, r]
allDol = [dol, dol, dol, dol]


names = ['John', 'Sally', 'Jane', 'Dan']
# first game order is always as set above
startingPlayer = 'winner'
startingStrategies = allDol
strategies = allRandom
gamemaster = GameMaster(names, strategies=strategies,
                        startingStrategies=startingStrategies,
                        startingPlayer=startingPlayer, maxGames=500)
result = gamemaster.run(trace=False)
pretty(result)
gamemaster.plotHelp()
