import pickle
from threading import Thread
import socket
from game import GameInstance


class Server:

    clients: list[socket.socket] = []
    nicknames: list[str] = []
    gameInstance: GameInstance

    def __init__(self):
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
        while True:
            try:
                # first message will be "start"
                message: str = client.recv(1024).decode()
                if message == "start":
                    self.gameInstance = GameInstance(self.nicknames)
                    for client in self.clients:
                        client.sendall(pickle.dumps(self.gameInstance))
                        print("Done packing")

            except:
                index = self.clients.index(client)
                self.clients.remove(client)
                client.close()
                nickname = self.nicknames[index]
                # self.broadcast(f"{nickname} left the lobby.")
                self.nicknames.remove(nickname)

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
