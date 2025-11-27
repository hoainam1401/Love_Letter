from Card import Card


class Countess(Card):
    value: int = 7
    name: str = "Countess"
    maxAvailable: int = 1

    def __init__(self):
        super().__init__()

    def play(self, player1, player2):
        pass
