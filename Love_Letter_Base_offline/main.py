import asyncio

import pygame

from ai import AiController
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
AI_SPEEDS = {"SLOW": 1700, "NORMAL": 900, "FAST": 350}


class LocalRoomGame:
    def __init__(self, username, roomCode, playerCount):
        self.username = username
        self.roomCode = roomCode
        self.playerCount = playerCount
        aiNames = []
        for index in range(1, playerCount):
            name = f"AI Player {index}"
            aiNames.append(f"{name} (Bot)" if name == username else name)
        names = [username] + aiNames
        self.game = GameInstance(names)
        self.ai = AiController(playerCount)
        self.aiSpeed = "NORMAL"
        self.aiPaused = False
        self.nextAiMoveAt = pygame.time.get_ticks() + AI_SPEEDS[self.aiSpeed]
        self.notifications = [f"Room {roomCode} created. Waiting for the first turn."]
        if self.game.removedCards:
            removed = ", ".join(card.name for card in self.game.removedCards)
            self.notifications.append(f"Face-up removed cards: {removed}.")
        self.pendingAction = None
        self.visualEvents = []

    def reset(self):
        self.game.resetTable()
        self.aiPaused = False
        self.ai.reset(self.playerCount)
        self.nextAiMoveAt = pygame.time.get_ticks() + AI_SPEEDS[self.aiSpeed]
        self.notifications = ["A new round has started."]
        if self.game.removedCards:
            removed = ", ".join(card.name for card in self.game.removedCards)
            self.notifications.append(f"Face-up removed cards: {removed}.")
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
            "heldCard": player.hand[1 - cardIndex].name,
            "target": None,
            "targetCard": None,
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
        self.pendingAction["targetCard"] = (
            self.pendingAction["heldCard"]
            if playerIndex == HUMAN_INDEX
            else self.game.playerList[playerIndex].hand[0].name
        )
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
            cardIndex = self.ai.chooseCard(self.game, actorIndex)
            self.pendingAction = {
                "actor": actorIndex,
                "card": self.game.currPlayer.hand[cardIndex].name,
                "heldCard": self.game.currPlayer.hand[1 - cardIndex].name,
                "target": None,
                "targetCard": None,
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
                targetIndex = self.ai.chooseTarget(
                    self.game,
                    actorIndex,
                    self.pendingAction["card"],
                    targets,
                )
                self.pendingAction["target"] = targetIndex
                self.pendingAction["targetCard"] = (
                    self.pendingAction["heldCard"]
                    if targetIndex == actorIndex
                    else self.game.playerList[targetIndex].hand[0].name
                )
                self.game.selectTarget(targetIndex)

        if self.game.gameState == "WAITING_FOR_GUESS":
            guess = self.ai.chooseGuess(
                self.game, actorIndex, self.pendingAction["target"]
            )
            self.pendingAction["guess"] = guess
            self.game.selectGuess(guess)

        self._finishAction()

        self._scheduleAi()

    def _scheduleAi(self):
        if (
            self.game.gameState != "GAME_ENDED"
            and self.game.currPlayerIndex != HUMAN_INDEX
        ):
            self.nextAiMoveAt = (
                pygame.time.get_ticks() + AI_SPEEDS[self.aiSpeed]
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
        self.ai.observeResolvedAction(
            self.game, actorIndex, cardName, targetIndex
        )
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
                "knockedOutIndexes": newlyKnockedOutIndexes,
                "guess": guess,
                "revealCard": (
                    action["targetCard"]
                    if cardName == "Priest" and actorIndex == HUMAN_INDEX
                    else None
                ),
                "discardedCard": (
                    self.game.lastForcedDiscard if cardName == "Prince" else None
                ),
                "drawnCard": (
                    target.hand[0].name
                    if cardName == "Prince" and target is not None and target.hand
                    else None
                ),
                "heldCard": action["heldCard"],
                "targetCard": action["targetCard"],
                "showSwapFaces": (
                    cardName == "King"
                    and targetIndex is not None
                    and HUMAN_INDEX in (actorIndex, targetIndex)
                ),
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
            discarded = self.game.lastForcedDiscard or "a card"
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
                    viewingDiscardIndex = None
                    gameLog.reset()
                    gameEndScreen.reset()
                    gameEffects.reset()
                    screen = SCREEN_GAME
            elif screen == SCREEN_GAME and roomGame is not None:
                gameLog.handle_event(event, roomGame.notifications, mousePos)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    roomGame = None
                    viewingDiscardIndex = None
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
                    viewingDiscardIndex = None
                    gameLog.reset()
                    gameEndScreen.reset()
                    gameEffects.reset()
                    screen = SCREEN_GAME
                elif action == "menu" or (
                    event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
                ):
                    roomGame = None
                    viewingDiscardIndex = None
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
