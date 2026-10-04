import json
import socket
import threading
from dataclasses import dataclass, field

from game import GameInstance


HOST = ""
PORT = 21011
MAX_PLAYERS = 4


@dataclass
class ClientSession:
    socket: socket.socket
    address: tuple
    username: str = ""
    roomCode: str = ""
    sendLock: threading.Lock = field(default_factory=threading.Lock)

    def send(self, message):
        payload = (json.dumps(message) + "\n").encode()
        with self.sendLock:
            self.socket.sendall(payload)


@dataclass
class Room:
    code: str
    clients: list[ClientSession] = field(default_factory=list)
    game: GameInstance | None = None


class Server:
    def __init__(self):
        self.rooms = {}
        self.lock = threading.RLock()
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((HOST, PORT))
        self.server.listen()
        print(f"Server is listening on 0.0.0.0:{PORT}")

    def run(self):
        try:
            while True:
                clientSocket, address = self.server.accept()
                session = ClientSession(clientSocket, address)
                threading.Thread(
                    target=self.handleClient, args=(session,), daemon=True
                ).start()
        finally:
            self.server.close()

    def handleClient(self, session):
        print(f"Connected: {session.address}")
        try:
            file = session.socket.makefile("r", encoding="utf-8")
            for line in file:
                if not line.strip():
                    continue
                message = json.loads(line)
                messageType = message.get("type")
                if messageType == "join":
                    self.joinRoom(session, message)
                elif messageType == "start":
                    self.startGame(session)
                elif messageType == "play":
                    self.playCard(session, message)
                else:
                    session.send({"type": "error", "message": "Unknown request"})
        except (ConnectionError, OSError, ValueError) as error:
            print(f"Client {session.address} disconnected: {error}")
        finally:
            self.removeClient(session)

    def joinRoom(self, session, message):
        username = str(message.get("username", "")).strip()[:20]
        roomCode = str(message.get("roomCode", "")).strip().upper()[:12]
        if not username or not roomCode:
            session.send(
                {"type": "error", "message": "Username and room code are required"}
            )
            return

        with self.lock:
            if session.roomCode:
                session.send({"type": "error", "message": "Already in a room"})
                return

            room = self.rooms.setdefault(roomCode, Room(roomCode))
            if room.game is not None:
                session.send({"type": "error", "message": "Game already in progress"})
                return
            if len(room.clients) >= MAX_PLAYERS:
                session.send({"type": "error", "message": "Room is full"})
                return
            if any(client.username == username for client in room.clients):
                session.send(
                    {"type": "error", "message": "That name is already in use"}
                )
                return

            session.username = username
            session.roomCode = roomCode
            room.clients.append(session)
            print(f"{username} joined room {roomCode}")
            self.sendLobby(room)

    def startGame(self, session):
        with self.lock:
            room = self.getRoom(session)
            if room is None:
                return
            if not room.clients or room.clients[0] is not session:
                session.send({"type": "error", "message": "Only the host can start"})
                return
            if not 2 <= len(room.clients) <= MAX_PLAYERS:
                session.send({"type": "error", "message": "Wait for 2-4 players"})
                return

            room.game = GameInstance([client.username for client in room.clients])
            self.sendGame(room)

    def playCard(self, session, message):
        with self.lock:
            room = self.getRoom(session)
            if room is None or room.game is None:
                session.send({"type": "error", "message": "No game is running"})
                return

            game = room.game
            playerIndex = room.clients.index(session)
            if playerIndex != game.currPlayerIndex:
                session.send({"type": "error", "message": "It is not your turn"})
                return

            try:
                cardIndex = int(message.get("selectedCardIndex", -1))
                targetIndex = int(message.get("selectedTargetIndex", -1))
                guess = int(message.get("selectedGuess", -1))
                if cardIndex < 0 or cardIndex >= len(game.currPlayer.hand):
                    raise ValueError("Invalid card")

                card = game.currPlayer.hand[cardIndex]
                if (
                    game.currPlayer.hasCountess
                    and (game.currPlayer.hasPrince or game.currPlayer.hasKing)
                    and card.name != "Countess"
                ):
                    raise ValueError("The Countess must be played")

                game.selectedCardIndex = cardIndex
                validTargets = [
                    index
                    for index in range(game.playerCount)
                    if game.isValidTarget(index)
                ]
                game.valid = len(validTargets)

                if game.valid and (game.cardNeedsTarget(card) or game.cardNeedsGuess(card)):
                    if targetIndex not in validTargets:
                        raise ValueError("Invalid target")
                    game.selectedTargetIndex = targetIndex
                if game.valid and game.cardNeedsGuess(card):
                    if not 2 <= guess <= 8:
                        raise ValueError("Invalid guess")
                    game.selectedGuess = guess

                game.executeCardPlay()
            except (TypeError, ValueError, IndexError) as error:
                session.send({"type": "error", "message": str(error)})
                self.sendGame(room)
                return

            self.sendGame(room)

    def sendLobby(self, room, message=""):
        players = [client.username for client in room.clients]
        for index, client in enumerate(room.clients):
            client.send(
                {
                    "type": "lobby",
                    "players": players,
                    "canStart": index == 0 and len(players) >= 2,
                    "message": message,
                }
            )

    def sendGame(self, room):
        game = room.game
        statuses = []
        tokens = []
        for player in game.playerList:
            if player.isKO:
                statuses.append("KO")
            elif player.isProtected:
                statuses.append("Protected")
            else:
                statuses.append("No Protection")
            tokens.append(player.winningTokenCount)

        for index, client in enumerate(room.clients):
            player = game.playerList[index]
            if game.gameState == "GAME_ENDED":
                clientState = "GAME_ENDED"
            elif game.currPlayerIndex == index:
                clientState = "WAITING_FOR_CARD"
            else:
                clientState = "WAITING_FOR_TURN"

            client.send(
                {
                    "type": "game",
                    "posInList": index,
                    "nameList": [item.username for item in room.clients],
                    "currIndex": game.currPlayerIndex,
                    "playerStatus": statuses,
                    "hasCountess": player.hasCountess,
                    "hasPrince": player.hasPrince,
                    "hasKing": player.hasKing,
                    "remainingCount": game.remainingCount(),
                    "gameState": clientState,
                    "handName": [card.name for card in player.hand],
                    "winningTokenCountList": tokens,
                    "winners": game.winners,
                    "discardPiles": [
                        [
                            {"name": card.name, "value": card.val}
                            for card in item.discardPile
                        ]
                        for item in game.playerList
                    ],
                }
            )

    def getRoom(self, session):
        room = self.rooms.get(session.roomCode)
        if room is None or session not in room.clients:
            session.send({"type": "error", "message": "Join a room first"})
            return None
        return room

    def removeClient(self, session):
        with self.lock:
            room = self.rooms.get(session.roomCode)
            if room is not None and session in room.clients:
                room.clients.remove(session)
                room.game = None
                if room.clients:
                    self.sendLobby(room, f"{session.username} left; game reset")
                else:
                    del self.rooms[room.code]
            try:
                session.socket.close()
            except OSError:
                pass


if __name__ == "__main__":
    Server().run()
