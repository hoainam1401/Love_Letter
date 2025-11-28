from card_pile import CardPile
from player import Player
import random


class GameInstance:
    playerList: list[Player] = []
    cardPile: CardPile
    currPlayer: Player  # current "Player"
    playerCount: int

    # these are avaiable in extended edition
    # jesterPair: tuple
    # sycophantForced: Player  # the "Player" that must be targeted in the next round

    # choose up to 2 "Player" at a time
    # maxPlayersChosen = 0
    # count of currently chosen "Player"
    # chosenPlayerCount = 0

    def __init__(self, nameList: list[str]):
        for name in nameList:
            self.playerList.append(Player(name))
        self.printPlayers()
        self.playerCount = len(nameList)
        self.cardPile = CardPile()
        self.currPlayer = self.playerList[random.choice(range(self.playerCount))]
        self.deal()
        print(f"Remaining cards are {self.remainingCount()}")

    def draw(self, player: Player):
        player.hand.append(self.cardPile.draw())

    def deal(self):
        for player in self.playerList:
            self.draw(player)
            print(f"{player.name} has {self.handInList(player)}")
        # self.draw(self.currPlayer)
        self.printPlayerHands()

    def nextPlayer(self):
        currPlayer = (self.playerList.index(self.currPlayer) + 1) % self.playerCount
        self.draw(self.currPlayer)

    def award(self, player: Player):
        player.winningTokenCount += 1

    def printPlayers(self):
        print("Players for this round are:")
        s = ""
        for player in self.playerList:
            s += player.name + ", "
        print(s)

    def printPlayerHands(self):
        print("Player hands are:")
        for player in self.playerList:
            print(f"{player.name} has {self.handInList(player)}")

    def handInList(self, player):
        handList = []
        handList.clear()
        for card in player.hand:
            print({card.name})
            handList.append(card.name)
        return handList

    def remainingCount(self):
        return len(self.cardPile.cardList)


# play test
if __name__ == "__main__":
    gameInstance = GameInstance(["A", "B", "C"])
