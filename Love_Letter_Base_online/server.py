import json
import socket
from threading import Lock, Thread

from card import Card
from game import GameInstance


class Room:
    def __init__(self, code):
        self.code = code
        self.clients = []
        self.nicknames = []
        self.game = None
        self.actionSeq = 0
        self.lastAction = None
        self.message = ""


class Server:
    def __init__(self, host="", port=21011):
        self.rooms = {}
        self.clientRooms = {}
        self.lock = Lock()
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((host, port))
        self.server.listen()
        print(f"Server is listening on {host or '0.0.0.0'}:{port}...")
        try:
            self.receive()
        finally:
            self.server.close()

    def _send(self, client, payload):
        client.sendall((json.dumps(payload) + "\n").encode())

    def _status(self, player):
        if player.isKO:
            return "KO"
        if player.isProtected:
            return "Protected"
        return "No Protection"

    def _privateAction(self, room, recipient):
        if room.lastAction is None:
            return None
        event = dict(room.lastAction)
        actor = event["actorIndex"]
        target = event.get("targetIndex")
        if event["cardName"] == "Priest" and recipient != actor:
            event["revealCard"] = None
        if event["cardName"] in ("Baron", "King") and recipient not in (actor, target):
            event.update(
                heldCard=None,
                targetCard=None,
                actorValue=None,
                targetValue=None,
                showComparison=False,
                showSwapFaces=False,
            )
        if event["cardName"] == "Prince" and recipient != target:
            event["drawnCard"] = None
        return event

    def _snapshot(self, room, recipient):
        if room.game is None:
            return {
                "type": "snapshot",
                "phase": "LOBBY",
                "roomCode": room.code,
                "posInList": recipient,
                "nameList": list(room.nicknames),
                "canStart": recipient == 0 and len(room.nicknames) >= 2,
                "actionSeq": room.actionSeq,
                "message": room.message,
            }

        game = room.game
        ended = game.gameState == "GAME_ENDED"
        state = (
            "GAME_ENDED"
            if ended
            else "WAITING_FOR_CARD"
            if game.currPlayerIndex == recipient
            else "WAITING_FOR_TURN"
        )
        return {
            "type": "snapshot",
            "phase": "GAME_ENDED" if ended else "PLAYING",
            "roomCode": room.code,
            "posInList": recipient,
            "nameList": [player.name for player in game.playerList],
            "currIndex": game.currPlayerIndex,
            "playerStatus": [self._status(player) for player in game.playerList],
            "remainingCount": game.remainingCount(),
            "gameState": state,
            "handName": [card.name for card in game.playerList[recipient].hand],
            "winningTokenCountList": [
                player.winningTokenCount for player in game.playerList
            ],
            "discardPiles": [
                [[card.name, card.val] for card in player.discardPile]
                for player in game.playerList
            ],
            "winners": list(game.winners),
            "finalHands": (
                [[card.name for card in player.hand] for player in game.playerList]
                if ended
                else [[] for _ in game.playerList]
            ),
            "actionSeq": room.actionSeq,
            "lastAction": self._privateAction(room, recipient),
        }

    def _broadcast(self, room):
        failed = []
        for index, client in enumerate(list(room.clients)):
            try:
                self._send(client, self._snapshot(room, index))
            except OSError:
                failed.append(client)
        for client in failed:
            self._remove(client)

    def _actionMessage(self, cardName, actorName, targetName, guess, knockedOut):
        if cardName == "Guard":
            result = " and knocked them out" if knockedOut else " but guessed incorrectly"
            return f"{actorName} played Guard on {targetName}, guessed {guess}{result}."
        if targetName:
            return f"{actorName} played {cardName} on {targetName}."
        return f"{actorName} played {cardName}."

    def _play(self, room, sender, payload):
        game = room.game
        if game is None or game.gameState == "GAME_ENDED":
            return
        actorIndex = room.clients.index(sender)
        if actorIndex != game.currPlayerIndex:
            return
        cardIndex = payload.get("cardIndex", -1)
        if not isinstance(cardIndex, int) or not 0 <= cardIndex < len(game.currPlayer.hand):
            return

        game.selectedCardIndex = cardIndex
        card = game.currPlayer.hand[cardIndex]
        if game.currPlayer.hasCountess and (game.currPlayer.hasPrince or game.currPlayer.hasKing) and card.name != "Countess":
            return
        validTargets = [index for index in range(game.playerCount) if game.isValidTarget(index)]
        needsTarget = game.cardNeedsTarget(card) or game.cardNeedsGuess(card)
        targetIndex = payload.get("targetIndex", -1)
        if needsTarget and validTargets and targetIndex not in validTargets:
            return
        guess = payload.get("guess", -1)
        if game.cardNeedsGuess(card) and validTargets and guess not in range(2, 9):
            return

        actor = game.currPlayer
        heldCard = actor.hand[1 - cardIndex].name if len(actor.hand) == 2 else None
        target = game.playerList[targetIndex] if isinstance(targetIndex, int) and targetIndex in range(game.playerCount) else None
        targetCard = target.hand[0].name if target is not None and target.hand else None
        beforeKo = [player.isKO for player in game.playerList]
        beforeDiscards = [len(player.discardPile) for player in game.playerList]

        game.selectedTargetIndex = targetIndex
        game.selectedGuess = guess
        game.valid = len(validTargets) if needsTarget else 1
        game.executeCardPlay()

        knockedOutIndexes = [
            index for index, player in enumerate(game.playerList)
            if player.isKO and not beforeKo[index]
        ]
        discardedCard = None
        drawnCard = None
        if card.name == "Prince" and target is not None:
            if len(target.discardPile) > beforeDiscards[targetIndex]:
                discardedCard = target.discardPile[-1].name
            if target.hand:
                drawnCard = target.hand[0].name
        targetName = target.name if target is not None else None
        room.actionSeq += 1
        room.lastAction = {
            "cardName": card.name,
            "actorIndex": actorIndex,
            "targetIndex": targetIndex if target is not None else None,
            "impactIndex": knockedOutIndexes[0] if knockedOutIndexes else (targetIndex if target is not None else actorIndex),
            "knockedOut": bool(knockedOutIndexes),
            "knockedOutIndexes": knockedOutIndexes,
            "guess": guess if guess in range(2, 9) else None,
            "revealCard": targetCard if card.name == "Priest" else None,
            "discardedCard": discardedCard,
            "drawnCard": drawnCard,
            "heldCard": heldCard,
            "targetCard": targetCard,
            "showSwapFaces": card.name == "King",
            "showComparison": card.name == "Baron",
            "actorValue": Card(heldCard).val if heldCard else None,
            "targetValue": Card(targetCard).val if targetCard else None,
            "message": self._actionMessage(card.name, actor.name, targetName, guess, bool(knockedOutIndexes)),
        }

    def _remove(self, client):
        room = self.clientRooms.pop(client, None)
        if room is None or client not in room.clients:
            return
        index = room.clients.index(client)
        wasHost = index == 0
        room.clients.pop(index)
        name = room.nicknames.pop(index)
        try:
            client.close()
        except OSError:
            pass

        if wasHost:
            self.rooms.pop(room.code, None)
            for other in list(room.clients):
                self.clientRooms.pop(other, None)
                try:
                    self._send(other, {"type": "room_closed", "message": "The host closed the room"})
                    other.close()
                except OSError:
                    pass
            room.clients.clear()
            return

        room.game = None
        room.lastAction = None
        room.message = f"{name} left. The table returned to the lobby."
        self._broadcast(room)

    def handle(self, client):
        reader = client.makefile("r", encoding="utf-8")
        try:
            for line in reader:
                payload = json.loads(line)
                with self.lock:
                    room = self.clientRooms.get(client)
                    if room is None:
                        break
                    messageType = payload.get("type")
                    if messageType == "start" and room.clients.index(client) == 0 and len(room.clients) >= 2 and room.game is None:
                        room.game = GameInstance(list(room.nicknames))
                        room.lastAction = None
                        room.message = ""
                    elif messageType == "action":
                        self._play(room, client, payload)
                    elif messageType == "rematch" and room.clients.index(client) == 0 and room.game is not None:
                        room.game.resetTable()
                        room.lastAction = None
                    self._broadcast(room)
        except (OSError, ValueError, json.JSONDecodeError) as error:
            print(f"Client disconnected: {error}")
        finally:
            reader.close()
            with self.lock:
                self._remove(client)

    def _readJoin(self, client):
        data = bytearray()
        while len(data) < 4096:
            chunk = client.recv(1)
            if not chunk:
                raise OSError("Connection closed before join")
            if chunk == b"\n":
                return json.loads(data.decode())
            data.extend(chunk)
        raise ValueError("Join request is too large")

    def _join(self, client, request):
        nickname = str(request.get("nickname", "")).strip()[:20]
        roomCode = str(request.get("roomCode", "")).strip().upper()[:12]
        mode = request.get("mode")
        if not nickname:
            return "Enter a player name"
        if not roomCode or not roomCode.isalnum():
            return "Room codes must use letters and numbers only"

        room = self.rooms.get(roomCode)
        if mode == "create":
            if room is not None:
                return "That room already exists"
            room = Room(roomCode)
            self.rooms[roomCode] = room
        elif mode == "join":
            if room is None:
                return "Room not found"
            if room.game is not None:
                return "That game has already started"
            if len(room.clients) >= 4:
                return "That room is full"
        else:
            return "Choose Create Room or Join Room"

        room.clients.append(client)
        room.nicknames.append(nickname)
        room.message = ""
        self.clientRooms[client] = room
        self._broadcast(room)
        print(f"{nickname} joined room {roomCode}")
        return None

    def receive(self):
        while True:
            client, _ = self.server.accept()
            try:
                request = self._readJoin(client)
                with self.lock:
                    error = self._join(client, request)
                if error:
                    self._send(client, {"type": "error", "message": error})
                    client.close()
                    continue
            except (OSError, ValueError, json.JSONDecodeError) as error:
                try:
                    self._send(client, {"type": "error", "message": str(error)})
                except OSError:
                    pass
                client.close()
                continue
            Thread(target=self.handle, args=(client,), daemon=True).start()


if __name__ == "__main__":
    Server()
