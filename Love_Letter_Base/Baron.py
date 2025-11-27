from Card import Card


class Baron(Card):
    value: int = 3
    name: str = "Baron"
    maxAvailable: int = 2

    def __init__(self):
        super().__init__()

    def play(self, player1, player2):
        pass
