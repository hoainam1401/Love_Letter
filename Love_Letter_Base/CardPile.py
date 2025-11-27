import random
from Card import Card
from Baron import Baron
from Countess import Countess
from Handmaid import Handmaid
from King import King
from Priest import Priest
from Guard import Guard
from Prince import Prince
from Princess import Princess


class CardPile:
    # Base game will have 16 / 14 cards, based on the total player count
    # If the game has less than 4 players, only 5 "Guard" cards are in the game,
    # else it has in total 8 "Guard" cards

    cardList: list[Card] = []

    # totalCards: int = 0

    def __init__(self):
        # Available in extended game
        # guardCount = Guard.maxAvailable if playerCount >= 5 else Guard.maxAvailableLess
        # for i in range(guardCount):

        for i in range(5):
            self.cardList.append(Guard())
        for i in range(2):
            self.cardList.append(Priest())
            self.cardList.append(Baron())
            self.cardList.append(Handmaid())
            self.cardList.append(Prince())
        self.cardList.append(King())
        self.cardList.append(Countess())
        self.cardList.append(Princess())
        random.shuffle(self.cardList)
        print("Card pile initiated:")
        self.printAll()

    def printAll(self):
        if len(self.cardList) > 0:
            strList = []
            for card in self.cardList:
                strList.append(card.name)
            print(strList)
        else:
            print("Card pile is empty.")
