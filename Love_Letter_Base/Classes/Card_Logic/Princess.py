from Love_Letter_Base.Classes.Card_Logic.Card import Card


class Princess(Card):
    value: int = 8
    name: str = "Princess"
    maxAvailable: int = 1

    def __init__(self):
        super().__init__()

    def play(player1, player2):
        pass
