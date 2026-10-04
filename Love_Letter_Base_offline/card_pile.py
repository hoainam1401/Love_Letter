import random
from card import Card


CARD_COUNTS = {
    "Guard": 5,
    "Priest": 2,
    "Baron": 2,
    "Handmaid": 2,
    "Prince": 2,
    "King": 1,
    "Countess": 1,
    "Princess": 1,
}


class CardPile:
    # Base game will have 16 cards
    cardList: list[Card]  # FIXED: Removed default [] to avoid shared state

    # totalCards: int = 0

    def __init__(self):
        # FIXED: Initialize cardList as instance variable
        self.cardList = []
        # Available in extended game
        # guardCount = Guard.maxAvailable if playerCount >= 5 else Guard.maxAvailableLess
        # for i in range(guardCount):

        for name, count in CARD_COUNTS.items():
            self.cardList.extend(Card(name) for _ in range(count))
        random.shuffle(self.cardList)
        # print("Card pile initiated:")
        # self.printAll()

    def draw(self):
        return self.cardList.pop()

    def printAll(self):
        if len(self.cardList) > 0:
            strList = []
            for card in self.cardList:
                strList.append(card.name)
            print(strList)
        else:
            print("Card pile is empty.")
