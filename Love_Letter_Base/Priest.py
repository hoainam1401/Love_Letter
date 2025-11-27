from Card import Card


class Priest(Card):
    value: int = 2
    name: str = "Priest"
    maxAvailable: int = 2

    def __init__(self):
        super().__init__()

    def play(self, player1, player2):
        pass
