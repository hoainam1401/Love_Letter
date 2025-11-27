from Card import Card


class King(Card):
    value: int = 6
    name: str = "King"
    maxAvailable: int = 1

    def __init__(self):
        super().__init__()

    def play(self, player1, player2):
        pass
