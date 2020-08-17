import random


class Piece:
    def __init__(self, values: tuple):
        assert values[0] in range(7) and values[1] in range(7)
        self.values = values
        self.value1 = values[0]
        self.value2 = values[1]
        self.sum = self.value1 + self.value2

    def equalTo(self, other):
        match = self.value1 == other.value1 and self.value2 in other.value2
        opp = self.value1 == other.value2 and self.value2 in other.value1
        return match or opp


class Player:
    def __init__(self, name: str):
        self.pieces = list()
        self.name = name

    def addPiece(self, myPiece: Piece):
        '''
        Adds a given piece from the player

        Returns whether or not it was present (True, False)
        '''
        assert len(self.pieces) in range(7)
        self.pieces.append(myPiece)

    def removePiece(self, myPiece):
        '''
        Removes a given piece from the player

        Returns whether or not it was present (True, False)
        '''
        for piece in self.pieces:
            if piece.equalTo(myPiece):
                self.pieces.remove(myPiece)
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
        self.table = list()
        end1, end2 = int(), int()
        self.players = players

    def shuffle(self):
        while len(self.currentAvailable) > 0:
            for player in self.players:
                randomPick = random.choice(self.currentAvailable)
                self.currentAvailable.remove(randomPick)
                player.addPiece(randomPick)

    def printStatus(self):
        for player in self.players:
            print(player.name)
            for piece in player.pieces:
                print(piece.values, end='')
            print('\n')


names = ['John', 'Sally', 'Jane', 'Dan']
players = list()
for name in names:
    players.append(Player(name))

game1 = Game(players)
game1.shuffle()
game1.printStatus()
