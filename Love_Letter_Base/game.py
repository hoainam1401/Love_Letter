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
    alivePlayerCount: int

    # these are avaiable in extended edition
    # jesterPair: tuple
    # sycophantForced: Player  # the "Player" that must be targeted in the next round

    # choose up to 2 "Player" at a time
    # maxPlayersChosen = 0
    # count of currently chosen "Player"
    # chosenPlayerCount = 0

    def __init__(self, nameList: list[str]):
        print("----------------------------------------")
        print("---------WELCOME TO LOVE LETTER---------")
        print("----------------------------------------")
        if len(nameList) < 2:
            raise ValueError("Game requires at least 2 players")
        if len(nameList) > 4:
            raise ValueError("Game supports maximum 4 players")

        for name in nameList:
            self.playerList.append(Player(name))
        self.printPlayers()
        self.playerCount = len(nameList)
        self.alivePlayerCount = len(nameList)
        self.cardPile = CardPile()
        self.currPlayerIndex = random.choice(range(self.playerCount))
        self.currPlayer = self.playerList[self.currPlayerIndex]
        self.deal()
        self.startGame()

    # -------------- GAME ROUND LOGIC ---------------

    # game runs based on user inputs in terminal
    def startGame(self):
        print("Game started!")
        while not self.isEndGame():
            currPlayer = self.currPlayer
            print(f"\nCurrent player is {currPlayer.name}")
            print(f"You have: {currPlayer.showCards()}")
            play: str = "-1"
            target: str = "-1"
            guessNum: str = "-1"
            self.printPlayerHands()
            # receive parameters through user input
            while int(play) not in range(1, 3):
                play = input("\nWhich one you want to play? 1 or 2: ")
            if (
                currPlayer.hand[int(play) - 1].name != "Handmaid"
                and currPlayer.hand[int(play) - 1].name != "Countess"
                and currPlayer.hand[int(play) - 1].name != "Princess"
            ):
                while int(target) not in range(1, self.playerCount + 1):
                    target = input(
                        f"Which player you wanna choose? Enter from 1 to {self.playerCount}: "
                    )
                while self.playerList[int(target) - 1].hasHandmaid:
                    target = input(
                        f"This player is protected, choose another player from 1 to {self.playerCount}: "
                    )
                while self.playerList[int(target) - 1].isKO:
                    target = input(
                        f"This player has been eliminated, choose another player from 1 to {self.playerCount}: "
                    )
            if currPlayer.hand[int(play) - 1].name == "Guard":
                while int(guessNum) not in range(2, 9):
                    guessNum = input(
                        f"Which number would you like to guess? Enter from 2 to 8: "
                    )
            self.play(int(play) - 1, int(target) - 1, int(guessNum))
            self.nextPlayer()

    def isEndGame(self):
        winner = Player("temp")
        if self.alivePlayerCount == 1:
            for player in self.playerList:
                if not player.isKO:
                    winner = player
        if len(self.cardPile.cardList) < 2:
            max = 0
            for player in self.playerList:
                if not player.isKO and player.hand[0].val > max:
                    max = player.hand[0].val
                    winner = player
        if self.alivePlayerCount == 1 or len(self.cardPile.cardList) < 2:
            print(f"{winner.name} is the winner!")
            return True

    def play(self, playedCardPosition: int, chosenPlayerPosition: int, guessedNum: int):
        playedCard: Card = self.currPlayer.hand[playedCardPosition]
        self.currPlayer.hand.remove(playedCard)

        # Print appropriate message based on card type
        if playedCard.name in ["Handmaid", "Countess", "Princess"]:
            print(f"Player {self.currPlayer.name} has played {playedCard.name}")
        elif playedCard.name == "Guard":
            chosenPlayer = self.playerList[chosenPlayerPosition]
            print(
                f"Player {self.currPlayer.name} has played {playedCard.name} towards {chosenPlayer.name} and guessed {guessedNum}"
            )
        else:
            chosenPlayer = self.playerList[chosenPlayerPosition]
            print(
                f"Player {self.currPlayer.name} has played {playedCard.name} towards {chosenPlayer.name}"
            )

        # Execute card effect
        if playedCard.name == "Guard":
            chosenPlayer = self.playerList[chosenPlayerPosition]
            self.eliminate(chosenPlayer, guessedNum)
        elif playedCard.name == "Priest":
            chosenPlayer = self.playerList[chosenPlayerPosition]
            self.peekHand(chosenPlayer)
        elif playedCard.name == "Baron":
            chosenPlayer = self.playerList[chosenPlayerPosition]
            self.compare(self.currPlayer, chosenPlayer)
        elif playedCard.name == "Handmaid":
            self.protect(self.currPlayer)
        elif playedCard.name == "Prince":
            chosenPlayer = self.playerList[chosenPlayerPosition]
            self.discard(chosenPlayer)
        elif playedCard.name == "King":
            chosenPlayer = self.playerList[chosenPlayerPosition]
            self.swap(self.currPlayer, chosenPlayer)
        elif playedCard.name == "Countess":
            pass
        elif playedCard.name == "Princess":
            self.KO(self.currPlayer)

    def draw(self, player: Player):
        player.hand.append(self.cardPile.draw())

    def deal(self):
        for player in self.playerList:
            self.draw(player)
        self.draw(self.currPlayer)
        # self.printPlayerHands()

    def nextPlayer(self):
        # print(f"current index: {self.currPlayerIndex}")
        # print(f"new index: {(self.currPlayerIndex + 1) % self.playerCount}")
        self.currPlayerIndex = (self.currPlayerIndex + 1) % self.playerCount
        self.currPlayer = self.playerList[self.currPlayerIndex]
        while self.currPlayer.isKO:
            self.currPlayerIndex = (self.currPlayerIndex + 1) % self.playerCount
            self.currPlayer = self.playerList[self.currPlayerIndex]
            self.currPlayer.hasHandmaid = False
        self.draw(self.currPlayer)

    def award(self, player: Player):
        player.winningTokenCount += 1

    def printPlayers(self):
        print("\nPlayers in this game are:")
        s = ""
        for player in self.playerList:
            s += player.name + ", "
        print(s)

    def printPlayerHands(self):
        print("Player hands are:")
        for index, player in enumerate(self.playerList):
            protected = "(is protected)" if player.hasHandmaid else ""
            ko = "(is KO)" if player.isKO else ""
            print(f"({index+1}) {player.name} has {player.showCards()}{protected}{ko}")

    def remainingCount(self):
        return len(self.cardPile.cardList)

    # ------------ CARDS LOGIC -----------------

    # for Guard Card
    # guess another player's card, if correct,
    # that player is knocked out of the round
    def eliminate(self, chosenPlayer: Player, guessedNum: int):
        if guessedNum == chosenPlayer.hand[0].val:
            self.KO(chosenPlayer)
        else:
            print("Guess not correct!")

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
        self.draw(chosenPlayer)

    # for King Card
    # current player swaps hand with another player
    def swap(self, currPlayer: Player, chosenPlayer: Player):
        temp = currPlayer.hand.copy()
        currPlayer.hand = chosenPlayer.hand.copy()
        chosenPlayer.hand = temp

    # for Countess Card
    # must discard if card "Prince" or "King"
    # is also on current player's hand

    # for Princess Card and other KO cards
    def KO(self, chosenPlayer: Player):
        chosenPlayer.isKO = True
        print(f"Player {chosenPlayer.name} is out of the round!")
        self.alivePlayerCount -= 1


# play test
if __name__ == "__main__":
    gameInstance = GameInstance(["A", "B", "C"])
    # gameInstance.play(
    #     1,
    #     gameInstance.playerList[random.choice([0, 1, 2])],
    #     random.choice([1, 2, 3, 4, 5, 6, 7, 8]),
    # )
