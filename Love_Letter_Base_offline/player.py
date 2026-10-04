from card import Card


class Player:
    name: str
    hand: list[Card]
    discardPile: list[Card]
    isKO: bool
    isProtected: bool
    hasPrince: int
    hasKing: int
    hasCountess: int
    finalPoint: int
    winningTokenCount: int

    def resetPlayer(self):
        self.hand: list[Card] = []
        self.discardPile: list[Card] = []
        self.isKO: bool = False
        self.isProtected: bool = False
        self.hasPrince: int = 0
        self.hasKing: int = 0
        self.hasCountess: int = 0
        self.finalPoint: int = 0

    def __init__(self, name: str):
        self.name = name
        self.winningTokenCount: int = 0
        self.resetPlayer()

    def discard(self, card: Card):
        self.discardPile.append(card)
        self.hand.remove(card)
        self.syncHandFlags()

    def syncHandFlags(self):
        self.hasPrince = sum(card.name == "Prince" for card in self.hand)
        self.hasKing = sum(card.name == "King" for card in self.hand)
        self.hasCountess = sum(card.name == "Countess" for card in self.hand)

    def showCards(self):
        s = ""
        for card in self.hand:
            s += card.name + " "
        return s
