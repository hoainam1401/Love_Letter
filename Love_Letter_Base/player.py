from card import Card


class Player:
    name: str = "Player 1"
    hand: list[Card] = []
    isKO: bool = False
    hasHandmaid: bool = False
    finalPoint: int = 0
    winningTokenCount: int = 0

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
