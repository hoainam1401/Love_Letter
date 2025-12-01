from abc import abstractmethod
from enum import Enum
from player import Player


class Card:
    name: str = ""
    val: int = 0
    img: str = ""

    def __init__(self, name):
        self.name = name
        if self.name == "Guard":
            self.val = 1
            self.img = f"images/{self.name}.png"
        elif self.name == "Priest":
            self.val = 2
            self.img = f"images/{self.name}.png"
        elif self.name == "Baron":
            self.val = 3
            self.img = f"images/{self.name}.png"
        elif self.name == "Handmaid":
            self.val = 4
            self.img = f"images/{self.name}.png"
        elif self.name == "Prince":
            self.val = 5
            self.img = f"images/{self.name}.png"
        elif self.name == "King":
            self.val = 6
            self.img = f"images/{self.name}.png"
        elif self.name == "Countess":
            self.val = 7
            self.img = f"images/{self.name}.png"
        elif self.name == "Princess":
            self.val = 8
            self.img = f"images/{self.name}.png"

    # for Guard Card
    # guess another player's card, if correct,
    # that player is knocked out of the round
    def eliminate(self, player1: Player, guessedNum: int):
        if guessedNum == player1.hand[0]:
            self.KO(player1)

    # for Priest Card
    # peek another player's hand
    def peekHand(self, player1: Player):
        print(f"{player1} has the card {player1.hand[0].toString()}")

    # for Baron Card
    # compare current player's card with another player
    # player with lower card is out
    def compare(self, player1: Player, player2: Player):
        if player1.hand[0].val > player2.hand[0].val:
            self.KO(player2)
        elif player1.hand[0].val < player2.hand[0].val:
            self.KO(player1)

    # for Handmaid Card
    # protect current player in one round
    # cannot be targeted by any card
    def protect(self, player1: Player):
        player1.hasHandmaid = True

    # for Prince Card
    # choose a player (including self) to discard
    # their card and draw a new one
    def discard(self, player1: Player, card: "Card"):
        player1.hand[0] = card

    # for King Card
    # current player swaps hand with another player
    def swap(self, player1: Player, player2: Player):
        temp = player1.hand[0]
        player1.hand = player2.hand
        player2.hand = temp

    # for Countess Card
    # must discard if card "Prince" or "King"
    # is also on current player's hand

    # for Princess Card and other KO cards
    def KO(self, player1: Player):
        player1.isKO = True

    def toString(self):
        return self.name
