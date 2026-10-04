import asyncio
import random

import pygame

from game import GameInstance
from gui import (
    FPS,
    GAME_LOG_RECT,
    GameEndScreen,
    GameEffects,
    GameLog,
    GameView,
    LoginScreen,
    PlayerSelectionScreen,
    draw_game_screen,
)


SCREEN_LOGIN = "LOGIN"
SCREEN_PLAYER_SELECT = "PLAYER_SELECT"
SCREEN_GAME = "GAME"
SCREEN_GAME_END = "GAME_END"
HUMAN_INDEX = 0
AI_SPEEDS = {"SLOW": 1400, "NORMAL": 700, "FAST": 250}
CARD_COUNTS = {
    "Guard": 5,
    "Priest": 2,
    "Baron": 2,
    "Handmaid": 2,
    "Prince": 2,
    "King": 1,
    "Countess": 1,
    "Princess": 1,
}
CARD_VALUES = {name: value for value, name in enumerate(CARD_COUNTS, start=1)}


class LocalRoomGame:
    def __init__(self, username, roomCode, playerCount):
        self.username = username
        self.roomCode = roomCode
        self.playerCount = playerCount
        names = [username] + [
            f"AI Player {index}" for index in range(1, playerCount)
        ]
        self.game = GameInstance(names)
        self.aiSpeed = "NORMAL"
        self.aiPaused = False
        self.aiKnownCards = {index: {} for index in range(1, playerCount)}
        self.nextAiMoveAt = pygame.time.get_ticks() + AI_SPEEDS[self.aiSpeed]
        self.notifications = [f"Room {roomCode} created. Waiting for the first turn."]
        self.pendingAction = None
        self.visualEvents = []

    def reset(self):
        self.game.resetTable()
        self.aiPaused = False
        self.aiKnownCards = {index: {} for index in range(1, self.playerCount)}
        self.nextAiMoveAt = pygame.time.get_ticks() + AI_SPEEDS[self.aiSpeed]
        self.notifications = ["A new round has started."]
        self.pendingAction = None
        self.visualEvents = []

    def view(self):
        statuses = []
        tokens = []
        for player in self.game.playerList:
            if player.isKO:
                statuses.append("KO")
            elif player.isProtected:
                statuses.append("Protected")
            else:
                statuses.append("No Protection")
            tokens.append(player.winningTokenCount)

        if self.game.gameState == "GAME_ENDED":
            state = "GAME_ENDED"
        elif self.game.currPlayerIndex != HUMAN_INDEX:
            state = "AI_TURN"
        else:
            state = self.game.gameState

        return GameView(
            roomCode=self.roomCode,
            names=[player.name for player in self.game.playerList],
            statuses=statuses,
            tokens=tokens,
            humanHand=[card.name for card in self.game.playerList[HUMAN_INDEX].hand],
            currentPlayer=self.game.currPlayerIndex,
            remainingCards=self.game.remainingCount(),
            gameState=state,
            selectedCardIndex=(
                self.game.selectedCardIndex
                if self.game.currPlayerIndex == HUMAN_INDEX
                else -1
            ),
            winners=list(self.game.winners),
            discardPiles=[
                [(card.name, card.val) for card in player.discardPile]
                for player in self.game.playerList
            ],
            finalHands=[
                [card.name for card in player.hand]
                for player in self.game.playerList
            ],
            notifications=list(self.notifications),
        )

    def toggleAiPaused(self):
        self.aiPaused = not self.aiPaused
        if not self.aiPaused:
            self._scheduleAi()

    def setAiSpeed(self, speed):
        if speed not in AI_SPEEDS:
            return
        self.aiSpeed = speed
        self._scheduleAi()

    def popVisualEvents(self):
        events = self.visualEvents
        self.visualEvents = []
        return events

    def validTargets(self):
        if (
            self.game.currPlayerIndex != HUMAN_INDEX
            or self.game.gameState != "WAITING_FOR_TARGET"
        ):
            return set()
        return {
            index
            for index in range(self.game.playerCount)
            if self.game.isValidTarget(index)
        }

    def selectCard(self, cardIndex):
        if self.game.currPlayerIndex != HUMAN_INDEX:
            return
        if self.game.gameState != "WAITING_FOR_CARD":
            return
        if cardIndex < 0 or cardIndex >= len(self.game.currPlayer.hand):
            return

        cardName = self.game.currPlayer.hand[cardIndex].name
        player = self.game.currPlayer
        if (
            player.hasCountess
            and (player.hasPrince or player.hasKing)
            and cardName != "Countess"
        ):
            self._notify("You must play the Countess while holding a Prince or King.")
            return
        beforeKo = [player.isKO for player in self.game.playerList]
        self.pendingAction = {
            "actor": HUMAN_INDEX,
            "card": cardName,
            "target": None,
            "guess": None,
            "beforeKo": beforeKo,
        }
        self.game.selectCard(cardIndex)
        if self.game.gameState == "WAITING_FOR_TARGET":
            self._notify(f"You chose {cardName}. Select a target player.")
        elif self.game.gameState == "WAITING_FOR_GUESS":
            self._notify(f"You chose {cardName}. Choose a guess from 2 to 8.")
        else:
            self._finishAction()
        self._scheduleAi()

    def selectTarget(self, playerIndex):
        if self.game.currPlayerIndex != HUMAN_INDEX or self.pendingAction is None:
            return
        if self.game.gameState != "WAITING_FOR_TARGET":
            return
        if not self.game.isValidTarget(playerIndex):
            self._notify("That player cannot be targeted.")
            return
        self.pendingAction["target"] = playerIndex
        self.game.selectTarget(playerIndex)
        if self.game.gameState == "WAITING_FOR_GUESS":
            targetName = self.game.playerList[playerIndex].name
            self._notify(f"Target: {targetName}. Now choose a guess.")
        else:
            self._finishAction()
        self._scheduleAi()

    def selectGuess(self, guess):
        if self.game.currPlayerIndex != HUMAN_INDEX or self.pendingAction is None:
            return
        if self.game.gameState != "WAITING_FOR_GUESS":
            return
        if guess < 2 or guess > 8:
            self._notify("Choose a guess from 2 to 8.")
            return
        self.pendingAction["guess"] = guess
        self.game.selectGuess(guess)
        self._finishAction()
        self._scheduleAi()

    def updateAi(self):
        if self.game.gameState == "GAME_ENDED":
            return
        if self.game.currPlayerIndex == HUMAN_INDEX:
            return
        if self.aiPaused:
            return
        if pygame.time.get_ticks() < self.nextAiMoveAt:
            return

        actorIndex = self.game.currPlayerIndex
        if self.game.gameState == "WAITING_FOR_CARD":
            cardIndex = self._chooseAiCard()
            self.pendingAction = {
                "actor": actorIndex,
                "card": self.game.currPlayer.hand[cardIndex].name,
                "target": None,
                "guess": None,
                "beforeKo": [player.isKO for player in self.game.playerList],
            }
            self.game.selectCard(cardIndex)

        if self.game.gameState == "WAITING_FOR_TARGET":
            targets = [
                index
                for index in range(self.game.playerCount)
                if self.game.isValidTarget(index)
            ]
            if targets:
                targetIndex = self._chooseAiTarget(actorIndex, targets)
                self.pendingAction["target"] = targetIndex
                self.game.selectTarget(targetIndex)

        if self.game.gameState == "WAITING_FOR_GUESS":
            guess = self._chooseAiGuess(
                actorIndex, self.pendingAction["target"]
            )
            self.pendingAction["guess"] = guess
            self.game.selectGuess(guess)

        self._finishAction()

        self._scheduleAi()

    def _chooseAiCard(self):
        player = self.game.currPlayer
        if player.hasCountess and (player.hasPrince or player.hasKing):
            for index, card in enumerate(player.hand):
                if card.name == "Countess":
                    return index

        actorIndex = self.game.currPlayerIndex
        knowledge = self.aiKnownCards[actorIndex]
        scores = []
        for index, card in enumerate(player.hand):
            otherCard = player.hand[1 - index]
            if card.name == "Princess":
                score = -100
            elif card.name == "Handmaid":
                score = 9
            elif card.name == "Guard":
                knownTarget = any(
                    name != "Guard" and self.game.isValidTarget(targetIndex)
                    for targetIndex, name in knowledge.items()
                )
                score = 12 if knownTarget else 6
            elif card.name == "Priest":
                score = 7
            elif card.name == "Baron":
                score = 8 if otherCard.val >= 5 else 2
            elif card.name == "Prince":
                score = 11 if "Princess" in knowledge.values() else 7
            elif card.name == "King":
                score = 8 if otherCard.val <= 3 else 3
            else:
                score = 1
            scores.append(score)

        bestScore = max(scores)
        choices = [index for index, score in enumerate(scores) if score == bestScore]
        return random.choice(choices)

    def _chooseAiTarget(self, actorIndex, targets):
        cardName = self.pendingAction["card"]
        knowledge = self.aiKnownCards[actorIndex]
        selectedCardIndex = self.game.selectedCardIndex
        remainingCard = self.game.currPlayer.hand[1 - selectedCardIndex]
        scores = {}
        for targetIndex in targets:
            knownCard = knowledge.get(targetIndex)
            score = random.random()
            if cardName == "Guard" and knownCard not in (None, "Guard"):
                score += 100
            elif cardName == "Priest" and knownCard is None:
                score += 20
            elif cardName == "Baron" and knownCard is not None:
                difference = remainingCard.val - CARD_VALUES[knownCard]
                score += 30 if difference > 0 else -30 if difference < 0 else 0
            elif cardName == "Prince":
                if targetIndex == actorIndex:
                    score -= 25
                    if remainingCard.name == "Princess":
                        score -= 100
                if knownCard == "Princess":
                    score += 100
                elif knownCard is not None:
                    score += CARD_VALUES[knownCard]
            elif cardName == "King" and knownCard is not None:
                score += (CARD_VALUES[knownCard] - remainingCard.val) * 5
            scores[targetIndex] = score
        return max(scores, key=scores.get)

    def _chooseAiGuess(self, actorIndex, targetIndex):
        knownCard = self.aiKnownCards[actorIndex].get(targetIndex)
        if knownCard is not None and knownCard != "Guard":
            return CARD_VALUES[knownCard]

        remaining = dict(CARD_COUNTS)
        for player in self.game.playerList:
            for card in player.discardPile:
                remaining[card.name] -= 1
        for card in self.game.currPlayer.hand:
            remaining[card.name] -= 1

        bestCount = max(remaining[name] for name in remaining if name != "Guard")
        guesses = [
            CARD_VALUES[name]
            for name, count in remaining.items()
            if name != "Guard" and count == bestCount
        ]
        return random.choice(guesses)

    def _scheduleAi(self):
        if (
            self.game.gameState != "GAME_ENDED"
            and self.game.currPlayerIndex != HUMAN_INDEX
        ):
            self.nextAiMoveAt = (
                pygame.time.get_ticks() + AI_SPEEDS[self.aiSpeed]
            )

    def _updateAiKnowledge(self, action):
        actorIndex = action["actor"]
        targetIndex = action["target"]
        cardName = action["card"]

        for knowledge in self.aiKnownCards.values():
            if cardName == "King":
                knowledge.pop(actorIndex, None)
                knowledge.pop(targetIndex, None)
            elif knowledge.get(actorIndex) == cardName:
                knowledge.pop(actorIndex, None)
            if cardName == "Prince":
                knowledge.pop(targetIndex, None)
            for playerIndex, player in enumerate(self.game.playerList):
                if player.isKO:
                    knowledge.pop(playerIndex, None)

        if actorIndex != HUMAN_INDEX and targetIndex is not None:
            target = self.game.playerList[targetIndex]
            if cardName == "Priest" and target.hand:
                self.aiKnownCards[actorIndex][targetIndex] = target.hand[0].name
            elif cardName == "King" and target.hand:
                self.aiKnownCards[actorIndex][targetIndex] = target.hand[0].name

        if (
            cardName == "King"
            and targetIndex not in (None, HUMAN_INDEX)
            and self.game.playerList[actorIndex].hand
        ):
            self.aiKnownCards[targetIndex][actorIndex] = (
                self.game.playerList[actorIndex].hand[0].name
            )

    def _finishAction(self):
        if self.pendingAction is None:
            return
        action = self.pendingAction
        actorIndex = action["actor"]
        cardName = action["card"]
        targetIndex = action["target"]
        guess = action["guess"]
        actorName = "You" if actorIndex == HUMAN_INDEX else self.game.playerList[actorIndex].name
        target = self.game.playerList[targetIndex] if targetIndex is not None else None
        self._updateAiKnowledge(action)
        newlyKnockedOutIndexes = [
            index
            for index, player in enumerate(self.game.playerList)
            if player.isKO and not action["beforeKo"][index]
        ]
        newlyKnockedOut = [
            self.game.playerList[index].name for index in newlyKnockedOutIndexes
        ]
        self.visualEvents.append(
            {
                "cardName": cardName,
                "actorIndex": actorIndex,
                "targetIndex": targetIndex,
                "impactIndex": (
                    newlyKnockedOutIndexes[0]
                    if newlyKnockedOutIndexes
                    else targetIndex
                ),
                "knockedOut": bool(newlyKnockedOut),
            }
        )

        if cardName == "Guard" and target is not None:
            if target.name in newlyKnockedOut:
                text = f"{actorName} played Guard, guessed {guess}, and knocked out {target.name}!"
            else:
                text = f"{actorName} played Guard on {target.name} and guessed {guess}. Wrong guess."
        elif cardName == "Priest" and target is not None:
            text = f"{actorName} played Priest on {target.name}."
            if actorIndex == HUMAN_INDEX and target.hand:
                text += f" {target.name} holds {target.hand[0].name}."
        elif cardName == "Baron" and target is not None:
            text = f"{actorName} compared hands with {target.name}."
            if newlyKnockedOut:
                text += f" {', '.join(newlyKnockedOut)} was knocked out."
            else:
                text += " The cards were tied."
        elif cardName == "Handmaid":
            text = f"{actorName} played Handmaid and is protected until the next turn."
        elif cardName == "Prince" and target is not None:
            discarded = target.discardPile[-1].name if target.discardPile else "a card"
            text = f"{actorName} made {target.name} discard {discarded}."
            if target.name in newlyKnockedOut:
                text += f" {target.name} was knocked out."
        elif cardName == "King" and target is not None:
            text = f"{actorName} played King and swapped hands with {target.name}."
        elif cardName == "Countess":
            text = f"{actorName} discarded the Countess."
        elif cardName == "Princess":
            text = f"{actorName} discarded the Princess and was knocked out."
        elif target is None:
            text = f"{actorName} played {cardName}; there was no valid target."
        else:
            text = f"{actorName} played {cardName} on {target.name}."

        self._notify(text)
        if self.game.gameState == "GAME_ENDED" and self.game.winners:
            self._notify(f"Round over. Winner: {', '.join(self.game.winners)}.")
        self.pendingAction = None

    def _notify(self, message):
        self.notifications.append(message)


async def main():
    clock = pygame.time.Clock()
    loginScreen = LoginScreen()
    playerSelectionScreen = PlayerSelectionScreen()
    gameEndScreen = GameEndScreen()
    gameEffects = GameEffects()
    gameLog = GameLog(GAME_LOG_RECT)
    screen = SCREEN_LOGIN
    roomGame = None
    username = ""
    roomCode = ""
    message = ""
    mousePos = (0, 0)
    cardRects = []
    playerRects = []
    numberButtons = []
    discardButtons = []
    aiControlButtons = []
    viewingDiscardIndex = None
    running = True

    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                continue
            if event.type == pygame.MOUSEMOTION:
                mousePos = event.pos

            if screen == SCREEN_LOGIN:
                credentials = loginScreen.handle_event(event)
                if credentials is not None:
                    username, roomCode = credentials
                    if not username or not roomCode:
                        message = "Enter both a player name and room code"
                    else:
                        screen = SCREEN_PLAYER_SELECT
                        message = ""
                        pygame.key.stop_text_input()
            elif screen == SCREEN_PLAYER_SELECT:
                selection = playerSelectionScreen.handle_event(event)
                if selection == "back" or (
                    event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
                ):
                    screen = SCREEN_LOGIN
                elif isinstance(selection, int):
                    roomGame = LocalRoomGame(username, roomCode, selection)
                    gameLog.reset()
                    gameEndScreen.reset()
                    gameEffects.reset()
                    screen = SCREEN_GAME
            elif screen == SCREEN_GAME and roomGame is not None:
                gameLog.handle_event(event, roomGame.notifications, mousePos)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    roomGame = None
                    screen = SCREEN_PLAYER_SELECT
                    continue
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for action, value, rect in aiControlButtons:
                        if rect.collidepoint(event.pos):
                            if action == "pause":
                                roomGame.toggleAiPaused()
                            elif action == "speed":
                                roomGame.setAiSpeed(value)
                            break
                    if not gameEffects.isBusy():
                        for index, rect in enumerate(cardRects):
                            if rect.collidepoint(event.pos):
                                roomGame.selectCard(index)
                                break
                        for playerIndex, rect in playerRects:
                            if rect.collidepoint(event.pos):
                                roomGame.selectTarget(playerIndex)
                                break
                        for number, rect in numberButtons:
                            if rect.collidepoint(event.pos):
                                roomGame.selectGuess(number)
                                break
                    for playerIndex, rect in discardButtons:
                        if rect.collidepoint(event.pos):
                            viewingDiscardIndex = (
                                None
                                if viewingDiscardIndex == playerIndex
                                else playerIndex
                            )
                            break
            elif screen == SCREEN_GAME_END and roomGame is not None:
                action = gameEndScreen.handle_event(event, roomGame.view(), mousePos)
                if action == "play_again":
                    roomGame.reset()
                    gameLog.reset()
                    gameEndScreen.reset()
                    gameEffects.reset()
                    screen = SCREEN_GAME
                elif action == "menu" or (
                    event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
                ):
                    roomGame = None
                    screen = SCREEN_PLAYER_SELECT

        if screen == SCREEN_LOGIN:
            loginScreen.draw(message)
        elif screen == SCREEN_PLAYER_SELECT:
            playerSelectionScreen.draw(username, roomCode)
        elif screen == SCREEN_GAME and roomGame is not None:
            for visualEvent in roomGame.popVisualEvents():
                gameEffects.trigger(visualEvent, roomGame.aiSpeed)
            if not gameEffects.isBusy():
                roomGame.updateAi()
            for visualEvent in roomGame.popVisualEvents():
                gameEffects.trigger(visualEvent, roomGame.aiSpeed)

            if roomGame.game.gameState == "GAME_ENDED" and not gameEffects.isBusy():
                screen = SCREEN_GAME_END
                gameEndScreen.start(roomGame.view())
                gameEndScreen.draw(roomGame.view())
            else:
                (
                    cardRects,
                    playerRects,
                    numberButtons,
                    discardButtons,
                    aiControlButtons,
                ) = draw_game_screen(
                    roomGame.view(),
                    mousePos,
                    roomGame.validTargets(),
                    gameLog,
                    roomGame.aiPaused,
                    roomGame.aiSpeed,
                    gameEffects,
                    viewingDiscardIndex,
                )
        elif screen == SCREEN_GAME_END and roomGame is not None:
            gameEndScreen.draw(roomGame.view())

        await asyncio.sleep(0)

    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
