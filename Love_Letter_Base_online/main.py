import asyncio
import json
import os
import queue
import socket
import threading
from dataclasses import replace

import pygame

from gui import (
    FPS,
    GameEndScreen,
    GameView,
    LoginScreen,
    LobbyScreen,
    draw_game_screen,
)


SERVER_HOST = os.environ.get("LOVE_LETTER_SERVER_HOST", "127.0.0.1")
SERVER_PORT = int(os.environ.get("LOVE_LETTER_SERVER_PORT", "21011"))

SCREEN_LOGIN = "LOGIN"
SCREEN_LOBBY = "LOBBY"
SCREEN_GAME = "GAME"


class NetworkClient:
    def __init__(self):
        self.socket = None
        self.messages = queue.SimpleQueue()
        self.sendLock = threading.Lock()
        self.generation = 0

    def connect(self, username, roomCode):
        self.close()
        connection = socket.create_connection((SERVER_HOST, SERVER_PORT), timeout=5)
        connection.settimeout(None)
        self.socket = connection
        self.generation += 1
        generation = self.generation
        self.send({"type": "join", "username": username, "roomCode": roomCode})
        threading.Thread(
            target=self._receive, args=(connection, generation), daemon=True
        ).start()

    def send(self, message):
        if self.socket is None:
            raise ConnectionError("Not connected to the server")
        with self.sendLock:
            connection = self.socket
            if connection is None:
                raise ConnectionError("Not connected to the server")
            payload = (json.dumps(message) + "\n").encode()
            connection.sendall(payload)

    def _receive(self, connection, generation):
        try:
            file = connection.makefile("r", encoding="utf-8")
            for line in file:
                if line.strip():
                    self.messages.put((generation, json.loads(line)))
        except (ConnectionError, OSError, ValueError) as error:
            self.messages.put(
                (generation, {"type": "error", "message": str(error)})
            )
        finally:
            self.messages.put((generation, {"type": "disconnected"}))

    def poll(self):
        messages = []
        while True:
            try:
                generation, message = self.messages.get_nowait()
                if generation == self.generation:
                    messages.append(message)
            except queue.Empty:
                return messages

    def close(self):
        self.generation += 1
        if self.socket is not None:
            try:
                self.socket.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            self.socket.close()
            self.socket = None


class OnlineGame:
    def __init__(self, network):
        self.network = network
        self.view = None
        self.selectedCardIndex = -1
        self.selectedTargetIndex = -1
        self.selectedGuess = -1

    def update(self, data, roomCode):
        self.view = GameView(
            room_code=roomCode,
            names=list(data.get("nameList", [])),
            statuses=list(data.get("playerStatus", [])),
            tokens=list(data.get("winningTokenCountList", [])),
            hand=list(data.get("handName", [])),
            position=int(data.get("posInList", -1)),
            current_player=int(data.get("currIndex", -1)),
            remaining_cards=int(data.get("remainingCount", 0)),
            game_state=data.get("gameState", "WAITING_FOR_TURN"),
            winners=list(data.get("winners", [])),
            discard_piles=[
                [
                    (card.get("name", ""), int(card.get("value", 0)))
                    for card in pile
                ]
                for pile in data.get("discardPiles", [])
            ],
        )
        self.hasCountess = int(data.get("hasCountess", 0))
        self.hasPrince = int(data.get("hasPrince", 0))
        self.hasKing = int(data.get("hasKing", 0))

    def cardNeedsTarget(self, cardName):
        return cardName in {
            "Assassin",
            "Jester",
            "Priest",
            "Baron",
            "Sycophant",
            "Prince",
            "King",
            "Dowager Queen",
        }

    def cardNeedsGuess(self, cardName):
        return cardName in {"Guard", "Bishop"}

    def cardAllowsSelf(self):
        if self.view is None or self.selectedCardIndex < 0:
            return False
        cardName = self.view.hand[self.selectedCardIndex]
        return cardName in {"Cardinal", "Baroness", "Sycophant", "Prince"}

    def validTargets(self):
        if self.view is None or self.view.game_state != "WAITING_FOR_TARGET":
            return set()

        targets = set()
        for index, status in enumerate(self.view.statuses):
            if status in {"KO", "Protected"}:
                continue
            if index != self.view.position or self.cardAllowsSelf():
                targets.add(index)
        return targets

    def selectCard(self, cardIndex):
        if self.view is None or self.view.game_state != "WAITING_FOR_CARD":
            return
        if cardIndex < 0 or cardIndex >= len(self.view.hand):
            return

        cardName = self.view.hand[cardIndex]
        if (
            self.hasCountess
            and (self.hasPrince or self.hasKing)
            and cardName != "Countess"
        ):
            return

        self.selectedCardIndex = cardIndex
        self.selectedTargetIndex = -1
        self.selectedGuess = -1

        if self.cardNeedsTarget(cardName) or self.cardNeedsGuess(cardName):
            self.view = replace(self.view, game_state="WAITING_FOR_TARGET")
            if not self.validTargets():
                self._sendPlay()
        else:
            self._sendPlay()

    def selectTarget(self, playerIndex):
        if playerIndex not in self.validTargets():
            return
        self.selectedTargetIndex = playerIndex
        cardName = self.view.hand[self.selectedCardIndex]
        if self.cardNeedsGuess(cardName):
            self.view = replace(self.view, game_state="WAITING_FOR_GUESS")
        else:
            self._sendPlay()

    def selectGuess(self, guess):
        if self.view is None or self.view.game_state != "WAITING_FOR_GUESS":
            return
        if 2 <= guess <= 8:
            self.selectedGuess = guess
            self._sendPlay()

    def _sendPlay(self):
        self.network.send(
            {
                "type": "play",
                "selectedCardIndex": self.selectedCardIndex,
                "selectedTargetIndex": self.selectedTargetIndex,
                "selectedGuess": self.selectedGuess,
            }
        )
        if self.view is not None:
            self.view = replace(self.view, game_state="WAITING_FOR_TURN")
        self.selectedCardIndex = -1
        self.selectedTargetIndex = -1
        self.selectedGuess = -1


async def main():
    clock = pygame.time.Clock()
    network = NetworkClient()
    onlineGame = OnlineGame(network)
    loginScreen = LoginScreen()
    lobbyScreen = LobbyScreen()
    gameEndScreen = GameEndScreen()

    screen = SCREEN_LOGIN
    username = ""
    roomCode = ""
    players = []
    canStart = False
    message = ""
    connecting = False
    running = True
    mousePos = (0, 0)
    cardRects = []
    playerRects = []
    numberButtons = []
    discardButtons = []
    viewingDiscardIndex = None

    while running:
        clock.tick(FPS)

        for serverMessage in network.poll():
            messageType = serverMessage.get("type")
            if messageType == "lobby":
                screen = SCREEN_LOBBY
                players = list(serverMessage.get("players", []))
                canStart = bool(serverMessage.get("canStart", False))
                message = serverMessage.get("message", "")
                connecting = False
            elif messageType == "game":
                onlineGame.update(serverMessage, roomCode)
                screen = SCREEN_GAME
                message = ""
            elif messageType == "error":
                message = serverMessage.get("message", "Unable to connect")
                connecting = False
            elif messageType == "disconnected" and screen != SCREEN_LOGIN:
                network.close()
                screen = SCREEN_LOGIN
                connecting = False
                message = "Connection closed"

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                continue
            if event.type == pygame.MOUSEMOTION:
                mousePos = event.pos

            if screen == SCREEN_LOGIN:
                credentials = loginScreen.handle_event(event)
                if credentials is not None and not connecting:
                    username, roomCode = credentials
                    if not username or not roomCode:
                        message = "Enter both a player name and room code"
                    else:
                        try:
                            connecting = True
                            message = "Connecting to the table..."
                            network.connect(username, roomCode)
                        except OSError as error:
                            connecting = False
                            message = f"Connection failed: {error}"

            elif screen == SCREEN_LOBBY:
                action = lobbyScreen.handle_event(event, canStart)
                if action == "start":
                    network.send({"type": "start"})
                elif action == "leave" or (
                    event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
                ):
                    network.close()
                    screen = SCREEN_LOGIN
                    message = ""

            elif screen == SCREEN_GAME:
                if onlineGame.view is not None and onlineGame.view.game_state == "GAME_ENDED":
                    action = gameEndScreen.handle_event(
                        event, onlineGame.view.position == 0
                    )
                    if action == "rematch":
                        network.send({"type": "start"})
                    elif action == "leave" or (
                        event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
                    ):
                        network.close()
                        screen = SCREEN_LOGIN
                        message = ""
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    network.close()
                    screen = SCREEN_LOGIN
                    message = ""
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for index, rect in enumerate(cardRects):
                        if rect.collidepoint(event.pos):
                            onlineGame.selectCard(index)
                            break
                    for playerIndex, rect in playerRects:
                        if rect.collidepoint(event.pos):
                            onlineGame.selectTarget(playerIndex)
                            break
                    for number, rect in numberButtons:
                        if rect.collidepoint(event.pos):
                            onlineGame.selectGuess(number)
                            break
                    for playerIndex, rect in discardButtons:
                        if rect.collidepoint(event.pos):
                            viewingDiscardIndex = (
                                None
                                if viewingDiscardIndex == playerIndex
                                else playerIndex
                            )
                            break

        if screen == SCREEN_LOGIN:
            loginScreen.draw(message, connecting)
        elif screen == SCREEN_LOBBY:
            lobbyScreen.draw(roomCode, players, canStart, message)
        elif onlineGame.view is not None:
            if onlineGame.view.game_state == "GAME_ENDED":
                gameEndScreen.draw(onlineGame.view, onlineGame.view.position == 0)
            else:
                cardRects, playerRects, numberButtons, discardButtons = (
                    draw_game_screen(
                        onlineGame.view,
                        mousePos,
                        onlineGame.validTargets(),
                        viewingDiscardIndex,
                    )
                )

        await asyncio.sleep(0)

    network.close()
    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
