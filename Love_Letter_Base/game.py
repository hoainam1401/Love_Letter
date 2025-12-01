from card import Card
from card_pile import CardPile
from player import Player
import random


class GameInstance:
    playerList: list[Player] = []
    cardPile: CardPile
    currPlayer: Player  # current "Player" in round
    currPlayerIndex: int  # position of "currPlayer"
    playerCount: int

    # these are avaiable in extended edition
    # jesterPair: tuple
    # sycophantForced: Player  # the "Player" that must be targeted in the next round

    # choose up to 2 "Player" at a time
    # maxPlayersChosen = 0
    # count of currently chosen "Player"
    # chosenPlayerCount = 0

    def __init__(self, nameList: list[str]):
        if len(nameList) < 2:
            raise ValueError("Game requires at least 2 players")
        if len(nameList) > 4:
            raise ValueError("Game supports maximum 4 players")
        
        for name in nameList:
            self.playerList.append(Player(name))
        self.printPlayers()
        self.playerCount = len(nameList)
        self.cardPile = CardPile()
        self.currPlayerIndex = random.choice(range(self.playerCount))
        self.currPlayer = self.playerList[self.currPlayerIndex]
        print(f"Remaining cards are {self.remainingCount()}")
        self.deal()
        print(f"Remaining cards are {self.remainingCount()}")

    def play(self, playedCardPosition: int, chosenPlayer: Player, guessedNum: int):
        playedCard: Card = self.currPlayer.hand[playedCardPosition]
        self.currPlayer.hand.remove(playedCard)
        print(
            f"Player {self.currPlayer.name} has played {playedCard.name} towards {chosenPlayer.name} and guessed {guessedNum}"
        )
        match playedCard.name:
            case "Guard":
                self.eliminate(chosenPlayer, guessedNum)
            case "Priest":
                self.peekHand(chosenPlayer)
            case "Baron":
                self.compare(self.currPlayer, chosenPlayer)
            case "Handmaid":
                self.protect(self.currPlayer)
            case "Prince":
                self.discard(chosenPlayer)
            case "King":
                self.swap(self.currPlayer, chosenPlayer)
            case "Countess":
                pass
            case "Princess":
                self.KO(self.currPlayer)

    def draw(self, player: Player):
        player.hand.append(self.cardPile.draw())
        print(f"Player '{player.name}' has {player.showCards()} ")

    def deal(self):
        for player in self.playerList:
            self.draw(player)
        self.draw(self.currPlayer)
        # self.printPlayerHands()

    def nextPlayer(self):
        self.currPlayerIndex = self.currPlayerIndex + 1 % self.playerCount
        self.currPlayer = self.playerList[self.currPlayerIndex]
        self.currPlayer.hasHandmaid = False
        self.draw(self.currPlayer)

    def award(self, player: Player):
        player.winningTokenCount += 1

    def printPlayers(self):
        print("Players in this game are:")
        s = ""
        for player in self.playerList:
            s += player.name + ", "
        print(s)

    def printPlayerHands(self):
        print("Player hands are:")
        for player in self.playerList:
            print(f"{player.name} has {player.showCards()}")

    def remainingCount(self):
        return len(self.cardPile.cardList)

    # ------------ CARDS LOGIC -----------------

    # for Guard Card
    # guess another player's card, if correct,
    # that player is knocked out of the round
    def eliminate(self, chosenPlayer: Player, guessedNum: int):
        if guessedNum == chosenPlayer.hand[0]:
            self.KO(chosenPlayer)

    # for Priest Card
    # peek another player's hand
    def peekHand(self, chosenPlayer: Player):
        print(f"{chosenPlayer.name} has the card {chosenPlayer.hand[0].name}")

    # for Baron Card
    # compare current player's card with another player
    # player with lower card is out
    def compare(self, currPlayer: Player, chosenPlayer: Player):
        if currPlayer.hand[0].val > chosenPlayer.hand[0].val:
            self.KO(chosenPlayer)
        elif currPlayer.hand[0].val < chosenPlayer.hand[0].val:
            self.KO(currPlayer)

    # for Handmaid Card
    # protect current player in one round
    # cannot be targeted by any card
    def protect(self, currPlayer: Player):
        currPlayer.hasHandmaid = True

    # for Prince Card
    # choose a player (including self) to discard
    # their card and draw a new one
    def discard(self, chosenPlayer: Player):
        chosenPlayer.hand = []

    # for King Card
    # current player swaps hand with another player
    def swap(self, currPlayer: Player, chosenPlayer: Player):
        temp = currPlayer.hand[0]
        currPlayer.hand = chosenPlayer.hand
        chosenPlayer.hand[0] = temp

    # for Countess Card
    # must discard if card "Prince" or "King"
    # is also on current player's hand

    # for Princess Card and other KO cards
    def KO(self, chosenPlayer: Player):
        chosenPlayer.isKO = True
        print(f"Player {chosenPlayer.name} is out of the round!")


# play test
if __name__ == "__main__":
    gameInstance = GameInstance(["A", "B", "C"])
    gameInstance.printPlayerHands()
    gameInstance.play(
        1,
        gameInstance.playerList[random.choice([0, 1, 2])],
        random.choice([1, 2, 3, 4, 5, 6, 7, 8]),
    )
