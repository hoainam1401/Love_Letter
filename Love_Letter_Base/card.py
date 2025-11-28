from abc import abstractmethod
from enum import Enum
from card_pile import CardPile
from player import Player


class Card:
    name: str = ""
    val: int = 0
    img: str = ""

    def __init__(self, name):
        self.name = name
        match self.name:
            case "Guard":
                self.val = 1
                self.img = f"images/{self.name}.png"
            case "Priest":
                self.val = 2
                self.img = f"images/{self.name}.png"
            case "Baron":
                self.val = 3
                self.img = f"images/{self.name}.png"
            case "Handmaid":
                self.val = 4
                self.img = f"images/{self.name}.png"
            case "Prince":
                self.val = 5
                self.img = f"images/{self.name}.png"
            case "King":
                self.val = 6
                self.img = f"images/{self.name}.png"
            case "Countess":
                self.val = 7
                self.img = f"images/{self.name}.png"
            case "Princess":
                self.val = 8
                self.img = f"images/{self.name}.png"

    # for Guard Card
    def eliminate(self, player1: Player, guessedNum: int):
        if guessedNum == player1.hand[0]:
            self.KO(player1)

    # for Priest Card
    def peekHand(self, player1: Player):
        print(f"{player1} has the card {player1.hand[0].toString()}")

    # for Baron Card
    def compare(self, player1: Player, player2: Player):
        if player1.hand[0].val > player2.hand[0].val:
            self.KO(player2)
        elif player1.hand[0].val < player2.hand[0].val:
            self.KO(player1)

    # for Handmaid Card
    def protect(self, player1: Player):
        player1.hasHandmaid = True

    # for Prince Card
    def discard(self, player1: Player, cardPile: CardPile):
        player1.hand[0] = cardPile.draw()

    # for King Card
    def swap(self, player1: Player, player2: Player):
        temp = player1.hand[0]
        player1.hand = player2.hand
        player2.hand = temp

    # for Countess Card

    # for Princess Card and other KO cards
    def KO(self, player1: Player):
        player1.isKO = True

    def toString(self):
        return self.name
