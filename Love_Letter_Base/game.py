from card_pile import CardPile
from player import Player


class GameInstance:
    playerList: list
    cardPile: CardPile
    currPlayer: Player  # current "Player"

    # these are avaiable in extended edition
    # jesterPair: tuple
    # sycophantForced: Player  # the "Player" that must be targeted in the next round

    maxPlayersChosen = 0  # choose up to 2 "Player" at a time

    # def award(self, player: Player):
    #     player.winningTokenCount += 1

    if __name__ == "__main__":
        cardPile = CardPile()
