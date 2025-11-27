from abc import abstractmethod


class Card:
    name: str = ""
    maxAvailable: int  # max amount available in a round

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def play(player1, player2):
        pass

    def toString(self):
        print(self.name)
