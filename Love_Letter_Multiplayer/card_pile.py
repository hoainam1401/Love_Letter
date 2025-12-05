import random
from card import Card


class CardPile:
    # Base game will have 16 cards
    cardList: list[Card]

    def __init__(self):
        self.cardList = []
        # Available in extended game
        # guardCount = Guard.maxAvailable if playerCount >= 5 else Guard.maxAvailableLess
        # for i in range(guardCount):

        for i in range(5):
            self.cardList.append(Card("Guard"))
        for i in range(2):
            self.cardList.append(Card("Priest"))
            self.cardList.append(Card("Baron"))
            self.cardList.append(Card("Handmaid"))
            self.cardList.append(Card("Prince"))
        self.cardList.append(Card("King"))
        self.cardList.append(Card("Countess"))
        self.cardList.append(Card("Princess"))
        random.shuffle(self.cardList)

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
