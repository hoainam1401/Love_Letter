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

    def __init__(self, name: str):
        self.name = name
        self.hand: list[Card] = []
        self.discardPile: list[Card] = []
        self.isKO: bool = False
        self.isProtected: bool = False
        self.hasPrince: int = 0
        self.hasKing: int = 0
        self.hasCountess: int = 0
        self.finalPoint: int = 0
        self.winningTokenCount: int = 0

    def discard(self, card: Card):
        self.discardPile.append(card)
        self.hand.remove(card)
        if card.name == "Princess":
            self.isKO = True

    def showCards(self):
        s = ""
        for card in self.hand:
            s += card.name + " "
        return s
