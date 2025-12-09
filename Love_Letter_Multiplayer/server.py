import pickle
from threading import Thread
import socket
from game import GameInstance
import json


class Server:

    clients: list[socket.socket]
    nicknames: list[str]
    gameInstance: GameInstance

    def __init__(self):
        self.clients = []
        self.nicknames = []
        self.gameInstance = None
        self.playerStatus = []
        self.host = ""  # local host
        self.port = 21011
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host, self.port))
        self.server.listen()
        print(f"Server is listening on {self.host}:{self.port}...")
        try:
            self.receive()
        finally:
            self.server.close()

    def broadcast(self, message: str):
        for client in self.clients:
            client.sendall((message + "\n").encode())

    def handle(self, client: socket.socket):
        message: str = client.recv(1024).decode()
        if message == "start":
            self.gameInstance = GameInstance(self.nicknames)
            playerStatus = []
            for player in self.gameInstance.playerList:
                if player.isKO:
                    playerStatus.append("KO")
                elif player.isProtected:
                    playerStatus.append("Protected")
                else:
                    playerStatus.append("No Protection")
            for i, client in enumerate(self.clients):
                gameStateClient = (
                    "WAITING_FOR_CARD"
                    if self.gameInstance.currPlayerIndex == i
                    else "WAITING_FOR_TURN"
                )
                handName = []
                for card in self.gameInstance.playerList[i].hand:
                    handName.append(card.name)
                dataDict = {
                    "posInList": i,
                    "nameList": self.nicknames,
                    "currIndex": self.gameInstance.currPlayerIndex,
                    "playerStatus": playerStatus,
                    "hasCountess": self.gameInstance.currPlayer.hasCountess,
                    "hasPrince": self.gameInstance.currPlayer.hasPrince,
                    "hasKing": self.gameInstance.currPlayer.hasKing,
                    "remainingCount": self.gameInstance.remainingCount(),
                    "gameState": gameStateClient,
                    "handName": handName,
                }
                print(dataDict)
                client.sendall(json.dumps(dataDict).encode())
                print("Done packing")
        while True:
            # unload data from client
            data = client.recv(1024).decode()
            dataDict = json.loads(data)
            print(f"received from client: {dataDict}")

    def receive(self):
        while True:
            client, address = self.server.accept()
            print(f"Connected with {str(address)}")
            nickname = client.recv(1024).decode()
            if client not in self.clients:
                self.nicknames.append(nickname)
                self.clients.append(client)
            print(f"Nickname of the client is {nickname}")
            print(f"{nickname} joined the lobby!")
            thread = Thread(target=self.handle, args=(client,))
            thread.start()


if __name__ == "__main__":
    Server()
