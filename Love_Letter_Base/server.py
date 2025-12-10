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
            client.sendall((message).encode())

    def sendToClients(self):
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

    def handle(self, client: socket.socket):
        index = self.clients.index(client)
        clientName = self.nicknames[index]
        print(f"listening on {clientName}")
        try:
            while True:
                print(f"waiting on {clientName}")
                typeOfMessage = client.recv(1024).decode()
                print(f"type of message is: {typeOfMessage}")
                if typeOfMessage == "message":
                    print("waiting for start")
                    startMessage = client.recv(1024).decode()
                    print(f"received from client: {startMessage}")
                    if startMessage == "start":
                        self.gameInstance = GameInstance(self.nicknames)
                        self.sendToClients()
                else:
                    # unload data from client
                    print(f"waiting for data back from client: {clientName}")
                    data = client.recv(1024).decode()
                    dataDict = json.loads(data)
                    print(f"received from client: {dataDict}")
                    # data = {"selectedCardIndex": 1, "selectedTargetIndex": 1, "selectedGuess": 6}
                    self.gameInstance.selectedCardIndex = dataDict["selectedCardIndex"]
                    self.gameInstance.selectedTargetIndex = dataDict[
                        "selectedTargetIndex"
                    ]
                    self.gameInstance.selectedGuess = dataDict["selectedGuess"]
                    self.gameInstance.valid = dataDict["valid"]
                    self.gameInstance.executeCardPlay()
                    self.sendToClients()
        except Exception as e:
            # remove leaving clients from list
            print(f"An error occurred on {clientName}: {e}")
            index = self.clients.index(client)
            self.clients.remove(client)
            nickname = self.nicknames[index]
            self.nicknames.remove(nickname)
            client.close()

    def receive(self):
        while True:
            client, address = self.server.accept()
            print(f"Connected with {str(address)}")
            nickname = client.recv(1024).decode()
            self.nicknames.append(nickname)
            self.clients.append(client)
            print(f"Nickname of the client is {nickname}")
            print(f"{nickname} joined the lobby!")
            thread = Thread(target=self.handle, args=(client,))
            thread.start()


if __name__ == "__main__":
    Server()
