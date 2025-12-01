from card import Card


class Player:
    name: str
    hand: list[Card]
    isKO: bool
    hasHandmaid: bool
    finalPoint: int
    winningTokenCount: int

    def __init__(self, name: str):
        self.name = name
        self.hand: list[Card] = []
        self.isKO: bool = False
        self.hasHandmaid: bool = False
        self.finalPoint: int = 0
        self.winningTokenCount: int = 0

    def showCards(self):
        s = ""
        for card in self.hand:
            s += card.name + " "
        return s
