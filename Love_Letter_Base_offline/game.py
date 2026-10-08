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
    winners: list[str]  # list of winner names
    sycophantForced: Player  # the "Player" that must be targeted in the next round
    # contains 2 players, the first is the betting one
    jesterPair: list[Player]
    # these are avaiable in extended edition

    # choose up to 2 "Player" at a time
    # maxPlayersChosen = 0
    # count of currently chosen "Player"
    # chosenPlayerCount = 0
    def resetTable(self):
        previousWinnerIndexes = getattr(self, "winnerIndexes", [])
        self.playerCount = len(self.playerList)
        self.alivePlayerCount = len(self.playerList)
        for player in self.playerList:
            player.resetPlayer()
        self.cardPile = CardPile()
        self.reservedCard = self.cardPile.draw()
        self.removedCards = []
        if self.playerCount == 2:
            self.removedCards = [self.cardPile.draw() for _ in range(3)]
        self.currPlayerIndex = (
            random.choice(previousWinnerIndexes)
            if previousWinnerIndexes
            else random.choice(range(self.playerCount))
        )
        self.currPlayer = self.playerList[self.currPlayerIndex]
        self.deal()
        self.gameState = "WAITING_FOR_CARD"
        self.selectedCardIndex = -1
        self.selectedTargetIndex = -1
        self.selectedGuess = -1
        self.valid = 0
        self.lastForcedDiscard = None
        self.winners = []
        self.winnerIndexes = []
        self.roundResolved = False

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
            "Jester",
            "Priest",
            "Baron",
            "Sycophant",
            "Prince",
            "King",
            "Queen",
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
        card = self.currPlayer.hand[self.selectedCardIndex]
        needsTarget = self.cardNeedsTarget(card) or self.cardNeedsGuess(card)
        if self.valid > 0 or not needsTarget:
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
            # Don't auto-restart - let the UI handle it

    def isEndGame(self):
        if self.roundResolved:
            return True

        self.winners = []
        self.winnerIndexes = []
        # Check if game should end
        game_over = self.alivePlayerCount == 1 or self.remainingCount() == 0

        if not game_over:
            return False

        # Determine winners
        # winner is the sole survivor
        if self.alivePlayerCount == 1:
            for index, player in enumerate(self.playerList):
                if not player.isKO:
                    self.winnerIndexes = [index]
                    break
        # calculate who has the highest score (when deck runs out)
        else:
            max_val = 0
            for player in self.playerList:
                if (
                    not player.isKO
                    and len(player.hand) > 0
                    and player.hand[0].val > max_val
                ):
                    max_val = player.hand[0].val

            # Find all players with the max value
            for index, player in enumerate(self.playerList):
                if (
                    not player.isKO
                    and len(player.hand) > 0
                    and player.hand[0].val == max_val
                ):
                    self.winnerIndexes.append(index)

        # Award tokens to winners
        self.winners = [self.playerList[index].name for index in self.winnerIndexes]
        for index in self.winnerIndexes:
            self.playerList[index].winningTokenCount += 1
        self.roundResolved = True

        return True

    # play a card with extra parameters, provide infomations
    # to execute card actions correctly
    def play(
        self,
        playedCardPosition: int,
        chosenPlayer1Position: int,
        chosenPlayer2Position: int,
        guessedNum: int,
    ):
        self.lastForcedDiscard = None
        playedCard: Card = self.currPlayer.hand[playedCardPosition]
        self.currPlayer.discard(playedCard)
        chosenPlayer1 = self.playerList[chosenPlayer1Position]
        chosenPlayer2 = self.playerList[chosenPlayer2Position]
        # Print appropriate message based on card type
        if playedCard.name in ["Handmaid", "Countess", "Princess"]:
            print(f"Player {self.currPlayer.name} has played {playedCard.name}")
        elif playedCard.name == "Guard":
            print(
                f"Player {self.currPlayer.name} has played {playedCard.name} towards {chosenPlayer1.name} and guessed {guessedNum}"
            )
        else:
            print(
                f"Player {self.currPlayer.name} has played {playedCard.name} towards {chosenPlayer1.name}"
            )
        # Execute card effect
        if playedCard.name == "Guard":
            chosenPlayer1 = self.playerList[chosenPlayer1Position]
            self.eliminate(chosenPlayer1, guessedNum)
        elif playedCard.name == "Priest":
            chosenPlayer1 = self.playerList[chosenPlayer1Position]
            self.peekHand(chosenPlayer1, None)
        elif playedCard.name == "Baron":
            chosenPlayer1 = self.playerList[chosenPlayer1Position]
            self.compare(self.currPlayer, chosenPlayer1)
        elif playedCard.name == "Handmaid":
            self.protect(self.currPlayer)
        elif playedCard.name == "Prince":
            chosenPlayer1 = self.playerList[chosenPlayer1Position]
            self.discard(chosenPlayer1)
        elif playedCard.name == "King":
            chosenPlayer1 = self.playerList[chosenPlayer1Position]
            self.swap(self.currPlayer, chosenPlayer1)
        elif playedCard.name == "Princess":
            self.KO(self.currPlayer)
        elif playedCard.name == "Jester":
            self.bet(self.currPlayer, chosenPlayer1)
        elif playedCard.name == "Cardinal":
            self.swap(chosenPlayer1, chosenPlayer2)
            # one more step to choose which player to peek their hand
        elif playedCard.name == "Baroness":
            self.peekHand(chosenPlayer1, chosenPlayer2)
        elif playedCard.name == "Sycophant":
            self.force(chosenPlayer1)
        elif playedCard.name == "Count":
            self.bonus(self.currPlayer)
        elif playedCard.name == "Constable":
            self.insure(self.currPlayer)
        elif playedCard.name == "Queen":
            self.compare_rev(self.currPlayer, chosenPlayer1)
        elif playedCard.name == "Bishop":
            self.guess(self.currPlayer, chosenPlayer1)

    def draw(self, player: Player):
        if self.cardPile.cardList:
            drawnCard = self.cardPile.draw()
        elif self.reservedCard is not None:
            drawnCard = self.reservedCard
            self.reservedCard = None
        else:
            return
        player.hand.append(drawnCard)
        player.syncHandFlags()

    # After starting game, deal for each player 1 card,
    # the first player gets extra 1 card
    def deal(self):
        for player in self.playerList:
            self.draw(player)
        self.draw(self.currPlayer)

    def nextPlayer(self):
        self.currPlayerIndex = (self.currPlayerIndex + 1) % self.playerCount
        self.currPlayer = self.playerList[self.currPlayerIndex]
        while self.currPlayer.isKO:
            self.currPlayerIndex = (self.currPlayerIndex + 1) % self.playerCount
            self.currPlayer = self.playerList[self.currPlayerIndex]
        self.currPlayer.isProtected = False
        self.draw(self.currPlayer)
        self.gameState = "WAITING_FOR_CARD"

    def award(self, player: Player):
        player.winningTokenCount += 1

    def printPlayers(self):
        print("\nPlayers in this game are:")
        s = ""
        for player in self.playerList:
            s += player.name + ", "
        print(s)

    def remainingCount(self):
        return len(self.cardPile.cardList)

    # ------------ CARDS LOGIC -----------------

    # for Guard Card
    # guess another player's card, if correct,
    # that player is knocked out of the round
    def eliminate(self, currPlayer: Player, chosenPlayer: Player, guessedNum: int):
        # if the chosen player has Assassin, the guessing one is KO out of the round
        if chosenPlayer.hand[0].name == "Assassin":
            self.KO(currPlayer)
        elif guessedNum == chosenPlayer.hand[0].val:
            self.KO(chosenPlayer)
        else:
            print("Guess not correct!")

    # for Priest and Baroness Card
    # peek another player's hand
    def peekHand(self, chosenPlayer1: Player, chosenPlayer2: Player):
        # if the played card is Priest
        if chosenPlayer2 is None:
            return chosenPlayer1.hand[0]
        # if the played card is Baroness
        else:
            return [chosenPlayer1.hand, chosenPlayer2.hand]

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
        discardedCard = chosenPlayer.hand[0]
        self.lastForcedDiscard = discardedCard.name
        chosenPlayer.discard(discardedCard)
        if discardedCard.name == "Princess":
            self.KO(chosenPlayer)
        else:
            self.draw(chosenPlayer)

    # for Cardinal and King Card
    # swaps hand of two players
    def swap(self, chosenPlayer1: Player, chosenPlayer2: Player):
        temp = chosenPlayer1.hand.copy()
        chosenPlayer1.hand = chosenPlayer2.hand.copy()
        chosenPlayer2.hand = temp
        chosenPlayer1.syncHandFlags()
        chosenPlayer2.syncHandFlags()

    # for Princess Card and other KO cards
    def KO(self, chosenPlayer: Player):
        if chosenPlayer.isKO:
            return
        chosenPlayer.isKO = True
        for card in chosenPlayer.hand.copy():
            chosenPlayer.discard(card)
        print(f"Player {chosenPlayer.name} is out of the round!")
        self.alivePlayerCount -= 1

    # for Jester Card
    # bets on the winning player
    def bet(self, currPlayer: Player, chosenPlayer: Player):
        self.jesterPair = [currPlayer, chosenPlayer]

    # for Sycophant Card
    # forces a player to be chosen next turn
    def force(self, chosenPlayer: Player):
        self.sycophantForced = chosenPlayer

    # for Count Card
    # increases final point by 1 at the end of the game
    def bonus(self, currPlayer: Player):
        currPlayer.hasCount += 1

    # for Constable Card
    # if player is knocked out with this card played, gain a winning token
    def insure(self, currPlayer: Player):
        currPlayer.hasConstable = True

    # for Queen Card
    # compare current player's card with another player
    # player with higher card is out (reversed comparing)
    def compare_rev(self, currPlayer: Player, chosenPlayer: Player):
        if currPlayer.hand[0].val > chosenPlayer.hand[0].val:
            self.KO(currPlayer)
        elif currPlayer.hand[0].val < chosenPlayer.hand[0].val:
            self.KO(chosenPlayer)

    # for Bishop Card
    # guess another player's card, if correct,
    # current player gains a winning token,
    # whether the guess was correct or not,
    # that player can choose to get a new card
    # by discarding the current card in hand
    def guess(self, currPlayer: Player, chosenPlayer: Player, guessedNum: int):
        if guessedNum == chosenPlayer.hand[0].val:
            currPlayer.winningTokenCount += 1
        else:
            print("Guess not correct!")


# play test
if __name__ == "__main__":
    gameInstance = GameInstance(["A", "B", "C"])
