from Love_Letter_Base.Classes.Card_Logic.Card import Card


class Guard(Card):
    value: int = 1
    name: str = "Guard"

    # extended game only
    # maxAvailable: int = 8
    # maxAvailableLess: int = 5

    def __init__(self):
        super().__init__()

    def play(player1, player2):
        pass
