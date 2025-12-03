from email import message
from pydoc import cli
from threading import Thread
import socket


class Server:

    clients: list[socket.socket] = []
    nicknames: list[str] = []

    def __init__(self):
        self.host = "0.0.0.0"  # local host
        self.port = 21012
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host, self.port))
        self.server.listen()
        print("Server is listening...")
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
                message: str = client.recv(1024).decode()
                messageSplit: list[str] = message.split(":")
                if messageSplit[1].strip() in ["start", "new game"]:
                    from lobby import Lobby

                    print("New game started.")
                    self.gameStarted = True
                    lobby = Lobby(self.nicknames, self)
            except:
                index = self.clients.index(client)
                self.clients.remove(client)
                client.close()
                nickname = self.nicknames[index]
                self.broadcast(f"{nickname} left the lobby")
                self.nicknames.remove(nickname)
                break

    def receive(self):
        while True:
            client, address = self.server.accept()
            print(f"Connected with {str(address)}")
            nickname = client.recv(1024).decode()
            if client not in self.clients:
                self.nicknames.append(nickname)
                self.clients.append(client)
            print(f"Nickname of the client is {nickname}")
            self.broadcast(f"{nickname} joined the lobby!")
            thread = Thread(target=self.handle, args=(client,))
            thread.start()


if __name__ == "__main__":
    Server()
