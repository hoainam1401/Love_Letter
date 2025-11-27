from Card import Card


class Handmaid(Card):
    value: int = 4
    name: str = "Handmaid"
    maxAvailable: int = 2

    def __init__(self):
        super().__init__()

    def play(self, player1, player2):
        pass
