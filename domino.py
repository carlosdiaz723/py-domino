import random


class Piece:
    def __init__(self, values: tuple):
        assert values[0] in range(7) and values[1] in range(7)
        self.values = values
        self.value1 = values[0]
        self.value2 = values[1]
        self.sum = self.value1 + self.value2

    def equalTo(self, other):
        match = self.value1 == other.value1 and self.value2 == other.value2
        opp = self.value1 == other.value2 and self.value2 == other.value1
        return match or opp


class Player:
    def __init__(self, name: str):
        self.hand = list()
        self.name = name

    def clearHand(self):
        for piece in self.hand:
            self.removePiece(piece)

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
        allPieces = [(6, 6),
                     (6, 5), (5, 5),
                     (6, 4), (5, 4), (4, 4),
                     (6, 3), (5, 3), (4, 3), (3, 3),
                     (6, 2), (5, 2), (4, 2), (3, 2), (2, 2),
                     (6, 1), (5, 1), (4, 1), (3, 1), (2, 1), (1, 1),
                     (6, 0), (5, 0), (4, 0), (3, 0), (2, 0), (1, 0), (0, 0)
                     ]
        self.master = list()
        for piece in allPieces:
            self.master.append(Piece(piece))
        self.currentAvailable = self.master
        self.table, self.end1, self.end2 = list(), int(), int()
        self.players = players
        self.metaWins = [0, 0, 0, 0]

    def reset(self):
        for player in self.players:
            player.clearHand()
        self.currentAvailable = self.master

    def shuffle(self):
        while len(self.currentAvailable) > 0:
            for player in self.players:
                randomPick = random.choice(self.currentAvailable)
                self.currentAvailable.remove(randomPick)
                player.addPiece(randomPick)

    def printStatus(self):
        for player in self.players:
            print(player.name)
            for piece in player.hand:
                print(piece.values, end='')
            print('\n')

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

    def count(self, player: Player):
        total = 0
        for piece in player.hand:
            total += piece.value1 + piece.value2
        return total

    def win(self, player: Player):
        score = 0
        for otherPlayer in self.players:
            if otherPlayer is not player:
                score += self.count(otherPlayer)
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

    def start(self, strategy='random', trace=False):
        passes = int()
        while True:
            passes = 0
            for player in self.players:
                possible = self.possiblePlays(player)
                if len(possible) == 0:
                    passes += 1
                    if trace:
                        print('Player: {} passes'.format(player.name))
                    continue

                # strategy switch
                if strategy == 'random':
                    piece, end = random.choice(possible)

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
                player.removePiece(piece)
                if trace:
                    print('Player: {} plays {}'.format(
                        player.name, str(piece.values)))
                    self.printTable()

                # check win
                if len(player.hand) == 0:
                    return self.win(player)
            if passes == 4:
                return self.closed()


names = ['John', 'Sally', 'Jane', 'Dan']
players = list()
for name in names:
    players.append(Player(name))

game1 = Game(players)
game1.reset()
game1.shuffle()
result = game1.start(trace=True)
print('\n{} wins with {} points'.format(result[0].name, result[1]))
