import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from ai import AiController
from card import CARD_VALUES, Card
from card_pile import CARD_COUNTS_EXT
from game import GameInstance


class GameRulesTest(unittest.TestCase):
    def makeGame(self, names=("Human", "AI")):
        with redirect_stdout(StringIO()):
            return GameInstance(list(names))

    def setTurn(self, game, playerIndex, hands):
        for player, cardNames in zip(game.playerList, hands):
            player.resetPlayer()
            player.hand = [Card(name) for name in cardNames]
            player.syncHandFlags()
        game.currPlayerIndex = playerIndex
        game.currPlayer = game.playerList[playerIndex]
        game.alivePlayerCount = len(game.playerList)
        game.gameState = "WAITING_FOR_CARD"
        game.roundResolved = False

    def testTwoPlayerSetupRemovesReserveAndThreeFaceUpCards(self):
        game = self.makeGame()

        self.assertIsNotNone(game.reservedCard)
        self.assertEqual(len(game.removedCards), 3)
        expectedRemaining = sum(CARD_COUNTS_EXT.values()) - 7
        self.assertEqual(game.remainingCount(), expectedRemaining)

    def testEveryCardHasAnImage(self):
        imageDirectory = Path(__file__).parent / "images"
        missing = [
            name
            for name in CARD_VALUES
            if not (imageDirectory / f"{name}.png").is_file()
        ]

        self.assertEqual(missing, [])

    def testHandmaidStillAppliesWhenNoOpponentCanBeTargeted(self):
        game = self.makeGame()
        self.setTurn(game, 0, (("Handmaid", "Guard"), ("Priest",)))
        game.playerList[1].isProtected = True

        with redirect_stdout(StringIO()):
            game.selectCard(0)

        self.assertTrue(game.playerList[0].isProtected)
        self.assertEqual(game.playerList[0].discardPile[0].name, "Handmaid")

    def testPrincessEliminationKeepsAliveCountSynchronized(self):
        game = self.makeGame()
        self.setTurn(game, 0, (("Princess", "Guard"), ("Priest",)))
        game.playerList[1].isProtected = True

        with redirect_stdout(StringIO()):
            game.selectCard(0)

        self.assertTrue(game.playerList[0].isKO)
        self.assertEqual(game.alivePlayerCount, 1)
        self.assertEqual(game.gameState, "GAME_ENDED")
        self.assertEqual(
            [card.name for card in game.playerList[0].discardPile],
            ["Princess", "Guard"],
        )

    def testRoundWinnerIsAwardedOnlyOnceAndStartsNextRound(self):
        game = self.makeGame()
        self.setTurn(game, 0, (("Guard",), ("Priest",)))

        with redirect_stdout(StringIO()):
            game.KO(game.playerList[1])
            self.assertTrue(game.isEndGame())
            self.assertTrue(game.isEndGame())

        self.assertEqual(game.playerList[0].winningTokenCount, 1)
        with redirect_stdout(StringIO()):
            game.resetTable()
        self.assertEqual(game.currPlayerIndex, 0)

    def testAiDoesNotChaseProtectedKnownPrincess(self):
        game = self.makeGame(("Human", "AI", "Other"))
        self.setTurn(
            game,
            1,
            (("Guard",), ("Prince", "Handmaid"), ("Princess",)),
        )
        game.playerList[2].isProtected = True
        ai = AiController(3)
        ai.knownCards[1][2] = "Princess"

        self.assertEqual(ai.chooseCard(game, 1), 1)

    def testAiGuessHandlesExtendedCardsInDiscardPile(self):
        game = self.makeGame(("Human", "AI", "Other"))
        self.setTurn(game, 1, (("Guard",), ("Guard", "Priest"), ("Princess",)))
        game.playerList[0].discardPile = [Card("Sycophant"), Card("Cardinal")]
        ai = AiController(3)
        ai.knownCards[1][0] = "Bishop"

        guess = ai.chooseGuess(game, 1, 0)

        self.assertIn(guess, range(2, 9))

    def testGuardGuessExecutesWithExtendedPlaySignature(self):
        game = self.makeGame()
        self.setTurn(game, 0, (("Guard", "Priest"), ("Baron",)))

        with redirect_stdout(StringIO()):
            game.selectCard(0)
            game.selectTarget(1)
            game.selectGuess(3)

        self.assertTrue(game.playerList[1].isKO)

    def testCardinalCollectsTwoDifferentTargets(self):
        game = self.makeGame(("Human", "First AI", "Second AI"))
        self.setTurn(
            game,
            0,
            (("Cardinal", "Guard"), ("Priest",), ("Princess",)),
        )

        with redirect_stdout(StringIO()):
            game.selectCard(0)
            game.selectTarget(1)
            self.assertEqual(game.gameState, "WAITING_FOR_TARGET")
            self.assertFalse(game.isValidTarget(1))
            game.selectTarget(2)

        self.assertEqual(game.playerList[1].hand[0].name, "Princess")
        self.assertEqual(game.playerList[2].hand[0].name, "Priest")

    def testPrinceTracksTheCardDiscardedBeforePrincessKnockout(self):
        game = self.makeGame()
        self.setTurn(game, 0, (("Prince", "Guard"), ("Princess",)))

        with redirect_stdout(StringIO()):
            game.selectCard(0)
            game.selectTarget(1)

        self.assertEqual(game.lastForcedDiscard, "Princess")
        self.assertTrue(game.playerList[1].isKO)

    def testKingSwapIsKnownOnlyToHumanTargetAndAiParticipant(self):
        game = self.makeGame(("Human", "Target AI", "Other AI"))
        self.setTurn(
            game,
            0,
            (("King", "Guard"), ("Princess",), ("Priest",)),
        )
        ai = AiController(3)
        ai.knownCards[1][0] = "Countess"
        ai.knownCards[2][0] = "Countess"
        ai.knownCards[2][1] = "Princess"

        game.swap(game.playerList[0], game.playerList[1])
        ai.observeResolvedAction(game, 0, "King", 1)

        self.assertEqual(ai.knownCards[1].get(0), "Princess")
        self.assertNotIn(0, ai.knownCards[2])
        self.assertNotIn(1, ai.knownCards[2])

    def testKingSwapBetweenAisStaysKnownOnlyToParticipants(self):
        game = self.makeGame(("Human", "First AI", "Second AI", "Other AI"))
        self.setTurn(
            game,
            1,
            (("Guard",), ("King", "Priest"), ("Princess",), ("Baron",)),
        )
        ai = AiController(4)
        ai.knownCards[3][1] = "Priest"
        ai.knownCards[3][2] = "Princess"

        game.playerList[1].discard(game.playerList[1].hand[0])
        game.swap(game.playerList[1], game.playerList[2])
        ai.observeResolvedAction(game, 1, "King", 2)

        self.assertEqual(ai.knownCards[1].get(2), "Priest")
        self.assertEqual(ai.knownCards[2].get(1), "Princess")
        self.assertNotIn(1, ai.knownCards[3])
        self.assertNotIn(2, ai.knownCards[3])


if __name__ == "__main__":
    unittest.main()
