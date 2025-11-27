import random
from Love_Letter_Base.Classes.Card_Logic.Baron import Baron
from Love_Letter_Base.Classes.Card_Logic.Countess import Countess
from Love_Letter_Base.Classes.Card_Logic.Handmaid import Handmaid
from Love_Letter_Base.Classes.Card_Logic.King import King
from Love_Letter_Base.Classes.Card_Logic.Priest import Priest
from Love_Letter_Base.Classes.Card_Logic.Guard import Guard
from Love_Letter_Base.Classes.Card_Logic.Prince import Prince
from Love_Letter_Base.Classes.Card_Logic.Princess import Princess


class CardPile:
    # Base game will have 16 / 14 cards, based on the total player count
    # If the game has less than 4 players, only 5 "Guard" cards are in the game,
    # else it has in total 8 "Guard" cards

    cardList: list = []
    totalCards: int = 0

    def __init__(self, playerCount: int):
        cardList: list = []

        # Available in extended game
        # guardCount = Guard.maxAvailable if playerCount >= 5 else Guard.maxAvailableLess
        # for i in range(guardCount):

        for i in range(5):
            cardList.append(Guard())
        for i in range(2):
            cardList.append(Priest())
            cardList.append(Baron())
            cardList.append(Handmaid())
            cardList.append(Prince())
        cardList.append(King())
        cardList.append(Countess())
        cardList.append(Princess())
        random.shuffle(cardList)

    def printAll(self):
        print(str(self.cardList))
