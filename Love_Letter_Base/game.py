from card import Card
from card_pile import CardPile
from player import Player
import random


class GameInstance:
    playerList: list[Player]  # FIXED: Removed default [] to avoid shared state
    cardPile: CardPile
    currPlayer: Player  # current "Player" in round
    currPlayerIndex: int  # position of "currPlayer"
    playerCount: int
    alivePlayerCount: int
    gameState: str
    # attributes to track playing card
    selectedCardIndex: int
    selectedTargetIndex: int
    selectedGuess: int
    valid: int  # track number of valid targets
    winners: list[Player]

    # these are avaiable in extended edition
    # jesterPair: tuple
    # sycophantForced: Player  # the "Player" that must be targeted in the next round

    # choose up to 2 "Player" at a time
    # maxPlayersChosen = 0
    # count of currently chosen "Player"
    # chosenPlayerCount = 0
    def resetTable(self):
        self.playerCount = len(self.playerList)
        self.alivePlayerCount = len(self.playerList)
        for player in self.playerList:
            player.resetPlayer()
        self.cardPile = CardPile()
        self.currPlayerIndex = random.choice(range(self.playerCount))
        self.currPlayer = self.playerList[self.currPlayerIndex]
        self.deal()
        self.printPlayerHands()
        self.gameState = "WAITING_FOR_CARD"
        self.selectedCardIndex = -1
        self.selectedTargetIndex = -1
        self.selectedGuess = -1

    def __init__(self, nameList: list[str]):
        print("----------------------------------------")
        print("---------WELCOME TO LOVE LETTER---------")
        print("----------------------------------------")
        if len(nameList) < 2:
            raise ValueError("Game requires at least 2 players")
        if len(nameList) > 4:
            raise ValueError("Game supports maximum 4 players")

        # FIXED: Initialize playerList as instance variable
        self.playerList = []
        for name in nameList:
            self.playerList.append(Player(name))
        self.printPlayers()
        self.resetTable()

    # -------------- GAME ROUND LOGIC ---------------

    # game runs based on user inputs in terminal
    def cardNeedsTarget(self, card: Card) -> bool:
        """Check if a card requires selecting a target player"""
        target_cards = [
            "Assassin",
            "Jester",
            "Priest",
            "Baron",
            "Sycophant",
            "Prince",
            "King",
            "Dowager Queen",
        ]
        return card.name in target_cards

    def cardNeedsTwoTargets(self, card: Card) -> bool:
        """Check if a card requires selecting 2 target players"""
        two_target_cards = ["Cardinal", "Baroness"]
        return card.name in two_target_cards

    def cardNeedsGuess(self, card: Card) -> bool:
        """Check if a card requires guessing a number"""
        return card.name in ["Guard", "Bishop"]

    # check if card can target self
    def cardSelfAllowed(self) -> bool:
        return self.currPlayer.hand[self.selectedCardIndex].name in [
            "Cardinal",
            "Baroness",
            "Sycophant",
            "Prince",
        ]

    def isValidTarget(self, playerIndex: int) -> bool:
        """Check if a player can be targeted"""
        if playerIndex < 0 or playerIndex >= self.playerCount:
            return False
        target = self.playerList[playerIndex]
        if target.isProtected:
            return False
        if target.isKO:
            return False
        if target == self.currPlayer:
            return self.cardSelfAllowed()
        return True

    # -------------- DURING PLAYER TURN ---------------
    def selectCard(self, cardIndex: int):
        """Called when player clicks a card in their hand"""
        if self.gameState != "WAITING_FOR_CARD":
            print("Not waiting for card selection!")
            return
        if (
            cardIndex < 0
            or cardIndex >= len(self.currPlayer.hand)
            or (
                self.currPlayer.hasCountess > 0
                and (self.currPlayer.hasPrince > 0 or self.currPlayer.hasKing > 0)
                and (self.currPlayer.hand[cardIndex].name != "Countess")
            )
        ):
            print("Invalid card index!")
            return

        # Store the selection
        self.selectedCardIndex = cardIndex
        card = self.currPlayer.hand[cardIndex]
        self.valid = 0
        for i in range(len(self.playerList)):
            if self.isValidTarget(i):
                self.valid += 1
        # Card doesn't need any info or no valid target, play it immediately
        if (
            not self.cardNeedsGuess(card) and not self.cardNeedsTarget(card)
        ) or self.valid == 0:
            self.executeCardPlay()
        else:
            self.gameState = "WAITING_FOR_TARGET"
            print(f"Card {card.name} needs a target. Select a player.")

    def selectTarget(self, playerIndex: int):
        """Called when player clicks a target player"""

        if self.gameState != "WAITING_FOR_TARGET":
            print("Not waiting for target selection!")
            return

        if not self.isValidTarget(playerIndex):
            print("Invalid target!")
            return

        # Store the selection
        self.selectedTargetIndex = playerIndex

        # Check if we also need a guess
        card = self.currPlayer.hand[self.selectedCardIndex]
        if self.cardNeedsGuess(card):
            self.gameState = "WAITING_FOR_GUESS"
            print("Now guess a number (2-8)")
        else:
            # We have everything we need
            self.executeCardPlay()

    def selectGuess(self, guessNum: int):
        """Called when player clicks a number button"""
        if self.gameState != "WAITING_FOR_GUESS":
            print("Not waiting for guess!")
            return

        if guessNum < 2 or guessNum > 8:
            print("Invalid guess! Must be 2-8")
            return

        # Store the selection
        self.selectedGuess = guessNum

        # Now we have everything
        self.executeCardPlay()

    def executeCardPlay(self):
        """Execute the play with all collected information"""
        if self.valid > 0:
            self.play(
                self.selectedCardIndex, self.selectedTargetIndex, self.selectedGuess
            )
        else:
            self.currPlayer.discard(self.currPlayer.hand[self.selectedCardIndex])
            print("Card canceled due to no valid target!")

        # Reset selections
        self.selectedCardIndex = -1
        self.selectedTargetIndex = -1
        self.selectedGuess = -1

        # Move to next player
        if not self.isEndGame():
            self.nextPlayer()
        else:
            print(f"winning players are: {self.winners}")
            self.gameState = "GAME_ENDED"
            # after game has ended, begins a new game
            # just for testing the tokens counting function
            self.resetTable()

    def isEndGame(self):
        self.winners = []
        # winner is the sole survivor
        if self.alivePlayerCount == 1:
            for player in self.playerList:
                if not player.isKO:
                    self.winners = [player.name]
                    player.winningTokenCount += 1
        # calculate who has the highest score
        # if multiple players have same score,
        # there would be multiple winners
        if self.remainingCount() < 2:
            max = 0
            for player in self.playerList:
                if not player.isKO and player.hand[0].val > max:
                    max = player.hand[0].val
                    self.winners.append(player)
                    player.winningTokenCount += 1
            for player in self.playerList:
                if not player.isKO and player.hand[0].val == max:
                    self.winners.append(player)
                    player.winningTokenCount += 1
        return self.alivePlayerCount == 1 or len(self.cardPile.cardList) < 2

    # play a card with extra parameters, provide infomations
    # to execute card actions correctly
    def play(self, playedCardPosition: int, chosenPlayerPosition: int, guessedNum: int):
        playedCard: Card = self.currPlayer.hand[playedCardPosition]
        self.currPlayer.discard(playedCard)
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
            self.currPlayer.hasPrince -= 1
            chosenPlayer = self.playerList[chosenPlayerPosition]
            self.discard(chosenPlayer)
        elif playedCard.name == "King":
            self.currPlayer.hasKing -= 1
            chosenPlayer = self.playerList[chosenPlayerPosition]
            self.swap(self.currPlayer, chosenPlayer)
        elif playedCard.name == "Countess":
            self.currPlayer.hasCountess -= 1
        elif playedCard.name == "Princess":
            self.KO(self.currPlayer)

    def draw(self, player: Player):
        drawnCard = self.cardPile.draw()
        print(f"\nPlayer {player.name} has drawn {drawnCard.name}")
        if drawnCard.name == "Prince":
            player.hasPrince += 1
        elif drawnCard.name == "King":
            player.hasKing += 1
        elif drawnCard.name == "Countess":
            player.hasCountess += 1
        player.hand.append(drawnCard)

    # After starting game, deal for each player 1 card,
    # the first player gets extra 1 card
    def deal(self):
        for player in self.playerList:
            self.draw(player)
        self.draw(self.currPlayer)
        # self.printPlayerHands()

    def nextPlayer(self):
        self.currPlayerIndex = (self.currPlayerIndex + 1) % self.playerCount
        self.currPlayer = self.playerList[self.currPlayerIndex]
        while self.currPlayer.isKO:
            self.currPlayerIndex = (self.currPlayerIndex + 1) % self.playerCount
            self.currPlayer = self.playerList[self.currPlayerIndex]
        self.currPlayer.isProtected = False
        self.draw(self.currPlayer)
        self.printPlayerHands()
        self.gameState = "WAITING_FOR_CARD"

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
            protected = "(is protected)" if player.isProtected else ""
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
        currPlayer.isProtected = True

    # for Prince Card
    # choose a player (including self) to discard
    # their card and draw a new one
    def discard(self, chosenPlayer: Player):
        isKO = chosenPlayer.discard(chosenPlayer.hand[0])
        if not chosenPlayer.isKO:
            self.draw(chosenPlayer)
        else:
            self.KO(chosenPlayer)

    # for King Card
    # current player swaps hand with another player
    def swap(self, currPlayer: Player, chosenPlayer: Player):
        temp = currPlayer.hand.copy()
        currPlayer.hand = chosenPlayer.hand.copy()
        chosenPlayer.hand = temp

    # for Princess Card and other KO cards
    def KO(self, chosenPlayer: Player):
        chosenPlayer.isKO = True
        print(f"Player {chosenPlayer.name} is out of the round!")
        self.alivePlayerCount -= 1


# play test
if __name__ == "__main__":
    gameInstance = GameInstance(["A", "B", "C"])
