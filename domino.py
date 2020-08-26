from pprint import pprint as pretty
import random


class Piece:
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
    def __init__(self, name: str):
        self.hand = list()
        self.name = name

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
    def __init__(self, players: list):
        self.currentAvailable = allPieces[:]
        self.table, self.end1, self.end2 = list(), int(), int()
        self.capicuaWin = False
        self.players = players

    def reset(self):
        for player in self.players:
            player.hand.clear()
        self.table.clear()
        self.capicuaWin = False
        self.end1, self.end2 = int(), int()
        self.currentAvailable = allPieces[:]

    def shuffle(self):
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
        for player in self.players:
            print(player.name)
            for piece in player.hand:
                print(piece.values, end='')
            print('\n')

    def isCapicua(self, piece: Piece):
        return piece.equalTo(Piece((self.end1, self.end2)))

    def possiblePlays(self, player: Player):
        '''
        Returns a list of possible pieces the player can play currently
        (as a list of tuples: (Piece, endNumber))
        '''
        possible = list()
        # opening move exception
        if len(self.table) == 0:
            return self.doubleOrLargest(player)
        for piece in player.hand:
            if self.end1 in piece.values:
                possible.append((piece, '1'))
            if self.end2 in piece.values:
                possible.append((piece, '2'))
        return possible

    def doubleOrLargest(self, player: Player):
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
        total = 0
        for piece in player.hand:
            total += piece.sum
        return total

    def win(self, player: Player, capicua=False):
        score = 0
        for otherPlayer in self.players:
            if otherPlayer is not player:
                score += self.count(otherPlayer)
        if capicua:
            self.capicuaWin = True
            score *= 2
        return player, score

    def printTable(self):
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
        lowest = 69
        lowestPlayer = Player('')
        for player in self.players:
            if self.count(player) < lowest:
                lowest = self.count(player)
                lowestPlayer = player
        return self.win(lowestPlayer)

    def start(self, strategy, startingStrategy, trace=False):
        passes = int()
        for _ in range(25):
            passes = 0
            for player in self.players:
                # first move exception
                if len(self.table) == 0:
                    piece = Piece((0, 0))
                    if startingStrategy == 'random':
                        piece = random.choice(player.hand)
                    elif startingStrategy == 'doubleOrLargest':
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
                if strategy == 'random':
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
    def __init__(self, playerNames: list, maxGames=1, strategy='random',
                 startingStrategy='random', maxScore=None, maxWins=None, startingPlayer='random'):
        self.playerNames = playerNames
        self.players = list()
        for name in playerNames:
            self.players.append(Player(name))
        self.maxGames = maxGames
        self.gamesPlayed = 0
        self.strategy = strategy
        self.startingStrategy = startingStrategy
        self.scores = [0, 0, 0, 0]
        self.wins = [0, 0, 0, 0]
        self.capicuaWins = [0, 0, 0, 0]
        self.game = Game(self.players)
        self.maxScore = maxScore
        self.maxWins = maxWins

    def finish(self):
        return {'players': self.playerNames,
                'wins': self.wins,
                'scores': self.scores,
                'gamesPlayed': self.gamesPlayed,
                'maxGames': self.maxGames,
                'capicuaWins': self.capicuaWins}

    def run(self, trace=False):
        for _ in range(self.maxGames):
            self.game.reset()
            self.game.shuffle()
            winner, score = self.game.start(
                self.strategy, self.startingStrategy, trace)
            if trace:
                print('Player: {} WINS'.format(winner.name))
            self.wins[self.players.index(winner)] += 1
            if self.game.capicuaWin:
                self.capicuaWins[self.players.index(winner)] += 1
            self.scores[self.players.index(winner)] += score
            if self.maxWins is not None:
                for w in self.wins:
                    if w >= self.maxWins:
                        return self.finish()
            if self.maxScore is not None:
                for s in self.scores:
                    if s >= self.maxScore:
                        return self.finish()
            self.gamesPlayed += 1
        return self.finish()


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


names = ['John', 'Sally', 'Jane', 'Dan']
gamemaster = GameMaster(names, maxGames=10000,
                        startingStrategy='random')
result = gamemaster.run()
pretty(result)
