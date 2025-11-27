from Love_Letter_Base.Classes.Card_Logic.Card import Card


class Prince(Card):
    value: int = 5
    name: str = "Prince"
    maxAvailable: int = 2

    def __init__(self):
        super().__init__()

    def play(player1, player2):
        pass
