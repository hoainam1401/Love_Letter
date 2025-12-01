class Player:
    name: str
    hand: list
    isKO: bool
    hasHandmaid: bool
    finalPoint: int
    winningTokenCount: int

    def __init__(self, name: str):
        self.name = name
        self.hand = []
        self.isKO = False
        self.hasHandmaid = False
        self.finalPoint = 0
        self.winningTokenCount = 0
