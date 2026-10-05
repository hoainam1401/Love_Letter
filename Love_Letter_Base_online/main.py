import asyncio
import json
import os
import queue
import socket
import threading

import pygame

from gui import (
    FPS,
    GAME_LOG_RECT,
    GameEffects,
    GameEndScreen,
    GameLog,
    GameView,
    LobbyScreen,
    LoginScreen,
    draw_game_screen,
)


DEFAULT_HOST = os.getenv("LOVE_LETTER_HOST", "127.0.0.1")
DEFAULT_PORT = int(os.getenv("LOVE_LETTER_PORT", "21011"))


class NetworkClient:
    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT):
        self.host = host
        self.port = port
        self.socket = None
        self.reader = None
        self.messages = queue.Queue()
        self.sendLock = threading.Lock()
        self.running = False

    def connect(self, nickname, roomCode, mode):
        self.socket = socket.create_connection((self.host, self.port), timeout=5)
        self.socket.settimeout(None)
        self.socket.sendall(
            (
                json.dumps(
                    {
                        "type": "join",
                        "nickname": nickname,
                        "roomCode": roomCode,
                        "mode": mode,
                    }
                )
                + "\n"
            ).encode()
        )
        self.reader = self.socket.makefile("r", encoding="utf-8")
        self.running = True
        threading.Thread(target=self._receive, daemon=True).start()

    def _receive(self):
        try:
            for line in self.reader:
                self.messages.put(json.loads(line))
        except (OSError, json.JSONDecodeError) as error:
            if self.running:
                self.messages.put({"type": "error", "message": str(error)})
        finally:
            if self.running:
                self.messages.put({"type": "disconnected", "message": "Server disconnected"})

    def send(self, messageType, **values):
        if not self.running:
            return
        payload = {"type": messageType, **values}
        try:
            with self.sendLock:
                self.socket.sendall((json.dumps(payload) + "\n").encode())
        except OSError as error:
            self.messages.put({"type": "error", "message": str(error)})

    def close(self):
        self.running = False
        if self.socket is not None:
            try:
                self.socket.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            self.socket.close()
        self.socket = None


def _order(snapshot):
    count = len(snapshot.get("nameList", []))
    localIndex = snapshot.get("posInList", 0)
    return [(localIndex + offset) % count for offset in range(count)]


def _parseServerAddress(address):
    address = address.strip()
    if not address:
        raise ValueError("Enter a server address")

    host = address
    port = DEFAULT_PORT
    if address.count(":") == 1:
        host, portText = address.rsplit(":", 1)
        if not host or not portText.isdigit():
            raise ValueError("Use a server address like 192.168.1.10:21011")
        port = int(portText)
    if not 1 <= port <= 65535:
        raise ValueError("Server port must be between 1 and 65535")
    return host, port


def _toViewIndex(serverIndex, localIndex, count):
    if serverIndex is None or not count:
        return None
    return (serverIndex - localIndex) % count


def _eventForView(event, localIndex, count):
    converted = dict(event)
    for key in ("actorIndex", "targetIndex", "impactIndex"):
        converted[key] = _toViewIndex(event.get(key), localIndex, count)
    converted["knockedOutIndexes"] = [
        _toViewIndex(index, localIndex, count)
        for index in event.get("knockedOutIndexes", [])
    ]
    return converted


def _makeView(snapshot, roomCode, localState, selectedCardIndex, notifications):
    order = _order(snapshot)
    names = snapshot.get("nameList", [])
    statuses = snapshot.get("playerStatus", [])
    tokens = snapshot.get("winningTokenCountList", [])
    discards = snapshot.get("discardPiles", [])
    finalHands = snapshot.get("finalHands", [])
    localIndex = snapshot.get("posInList", 0)
    current = _toViewIndex(snapshot.get("currIndex"), localIndex, len(order))
    return GameView(
        roomCode=roomCode,
        names=[names[index] for index in order],
        statuses=[statuses[index] for index in order],
        tokens=[tokens[index] for index in order],
        humanHand=list(snapshot.get("handName", [])),
        currentPlayer=current if current is not None else -1,
        remainingCards=snapshot.get("remainingCount", 0),
        gameState=localState or snapshot.get("gameState", "WAITING_FOR_TURN"),
        selectedCardIndex=selectedCardIndex,
        winners=list(snapshot.get("winners", [])),
        discardPiles=[discards[index] for index in order],
        finalHands=[finalHands[index] for index in order],
        notifications=list(notifications),
    )


def _validTargets(view, cardName):
    selfAllowed = cardName == "Prince"
    return {
        index for index, status in enumerate(view.statuses)
        if status not in ("KO", "Protected") and (index != 0 or selfAllowed)
    }


async def main():
    clock = pygame.time.Clock()
    loginScreen = LoginScreen(f"{DEFAULT_HOST}:{DEFAULT_PORT}")
    lobbyScreen = LobbyScreen()
    gameEndScreen = GameEndScreen()
    gameEffects = GameEffects()
    gameLog = GameLog(GAME_LOG_RECT)
    network = None
    snapshot = None
    screen = "LOGIN"
    username = ""
    roomCode = ""
    message = ""
    notifications = []
    lastActionSeq = 0
    selectedCardIndex = -1
    selectedTargetIndex = None
    localState = None
    viewingDiscardIndex = None
    mousePos = (0, 0)
    cardRects = []
    playerRects = []
    numberButtons = []
    discardButtons = []
    running = True

    while running:
        clock.tick(FPS)
        if network is not None:
            activeNetwork = network
            while True:
                try:
                    incoming = activeNetwork.messages.get_nowait()
                except queue.Empty:
                    break
                if incoming.get("type") == "snapshot":
                    snapshot = incoming
                    roomCode = snapshot.get("roomCode", roomCode)
                    message = snapshot.get("message", "")
                    phase = snapshot.get("phase")
                    if phase == "LOBBY":
                        screen = "LOBBY"
                    else:
                        screen = "GAME"
                    actionSeq = snapshot.get("actionSeq", 0)
                    if actionSeq > lastActionSeq and snapshot.get("lastAction"):
                        event = snapshot["lastAction"]
                        notifications.append(event.get("message", f"{event['cardName']} played."))
                        gameEffects.trigger(
                            _eventForView(
                                event,
                                snapshot.get("posInList", 0),
                                len(snapshot.get("nameList", [])),
                            )
                        )
                        selectedCardIndex = -1
                        selectedTargetIndex = None
                        localState = None
                    lastActionSeq = max(lastActionSeq, actionSeq)
                elif incoming.get("type") in ("error", "room_closed"):
                    message = incoming.get("message", "Connection error")
                    if network is not None:
                        network.close()
                    network = None
                    screen = "LOGIN"
                    snapshot = None
                elif incoming.get("type") == "disconnected":
                    if screen != "LOGIN":
                        message = incoming.get("message", "Server disconnected")
                        screen = "LOGIN"
                        snapshot = None

        view = None
        if snapshot is not None and snapshot.get("phase") != "LOBBY":
            view = _makeView(snapshot, roomCode, localState, selectedCardIndex, notifications)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                continue
            if event.type == pygame.MOUSEMOTION:
                mousePos = event.pos

            if screen == "LOGIN":
                credentials = loginScreen.handle_event(event)
                if credentials is not None:
                    mode, username, roomCode, serverAddress = credentials
                    if not username or not roomCode or not serverAddress:
                        message = "Enter a server, player name, and room code"
                    else:
                        try:
                            host, port = _parseServerAddress(serverAddress)
                            network = NetworkClient(host, port)
                            network.connect(username, roomCode, mode)
                            message = ""
                            screen = "LOBBY"
                        except (OSError, ValueError) as error:
                            network = None
                            message = f"Could not connect: {error}"
            elif screen == "LOBBY" and snapshot is not None:
                action = lobbyScreen.handle_event(event, snapshot.get("canStart", False))
                if action == "start":
                    network.send("start")
                elif action == "back":
                    network.close()
                    network = None
                    snapshot = None
                    screen = "LOGIN"
            elif screen == "GAME" and view is not None:
                gameLog.handle_event(event, view.notifications, mousePos)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    network.close()
                    network = None
                    snapshot = None
                    screen = "LOGIN"
                    continue
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if not gameEffects.isBusy():
                        for index, rect in enumerate(cardRects):
                            if not rect.collidepoint(event.pos) or view.gameState != "WAITING_FOR_CARD":
                                continue
                            cardName = view.humanHand[index]
                            if "Countess" in view.humanHand and ("Prince" in view.humanHand or "King" in view.humanHand) and cardName != "Countess":
                                notifications.append("You must play the Countess while holding a Prince or King.")
                                break
                            selectedCardIndex = index
                            targets = _validTargets(view, cardName)
                            if cardName in ("Guard", "Priest", "Baron", "Prince", "King") and targets:
                                localState = "WAITING_FOR_TARGET"
                            else:
                                network.send("action", cardIndex=index, targetIndex=-1, guess=-1)
                                localState = "WAITING_FOR_TURN"
                            break
                        for targetViewIndex, rect in playerRects:
                            if not rect.collidepoint(event.pos) or localState != "WAITING_FOR_TARGET":
                                continue
                            selectedTargetIndex = _order(snapshot)[targetViewIndex]
                            cardName = view.humanHand[selectedCardIndex]
                            if cardName == "Guard":
                                localState = "WAITING_FOR_GUESS"
                            else:
                                network.send("action", cardIndex=selectedCardIndex, targetIndex=selectedTargetIndex, guess=-1)
                                localState = "WAITING_FOR_TURN"
                            break
                        for number, rect in numberButtons:
                            if rect.collidepoint(event.pos) and localState == "WAITING_FOR_GUESS":
                                network.send("action", cardIndex=selectedCardIndex, targetIndex=selectedTargetIndex, guess=number)
                                localState = "WAITING_FOR_TURN"
                                break
                    for playerIndex, rect in discardButtons:
                        if rect.collidepoint(event.pos):
                            viewingDiscardIndex = None if viewingDiscardIndex == playerIndex else playerIndex
                            break
            elif screen == "GAME_END" and view is not None:
                action = gameEndScreen.handle_event(event, view, mousePos)
                if action == "play_again":
                    network.send("rematch")
                    gameEndScreen.reset()
                elif action == "menu":
                    network.close()
                    network = None
                    snapshot = None
                    screen = "LOGIN"

        if screen == "LOGIN":
            loginScreen.draw(message)
        elif screen == "LOBBY":
            names = snapshot.get("nameList", []) if snapshot else []
            canStart = snapshot.get("canStart", False) if snapshot else False
            lobbyScreen.draw(username, roomCode, names, canStart, message)
        elif screen == "GAME" and view is not None:
            validTargets = set()
            if localState == "WAITING_FOR_TARGET" and selectedCardIndex >= 0:
                validTargets = _validTargets(view, view.humanHand[selectedCardIndex])
            cardRects, playerRects, numberButtons, discardButtons, _ = draw_game_screen(
                view,
                mousePos,
                validTargets,
                gameLog,
                False,
                "NORMAL",
                gameEffects,
                viewingDiscardIndex,
            )
            if snapshot.get("phase") == "GAME_ENDED" and not gameEffects.isBusy():
                screen = "GAME_END"
                gameEndScreen.start(view)
        elif screen == "GAME_END" and view is not None:
            gameEndScreen.draw(view)

        await asyncio.sleep(0)

    if network is not None:
        network.close()
    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
