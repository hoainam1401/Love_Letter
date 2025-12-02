import threading
import socket


class Server:

    clients: list[socket.socket] = []
    nicknames: list[str] = []
    gameStarted = False

    def __init__(self):
        self.host = "0.0.0.0"  # local host
        self.port = 21012
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host, self.port))
        self.server.listen()
        self.gameStarted = False
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
                if messageSplit[1].strip() == "start":
                    from lobby import Lobby

                    lobby = Lobby(self.nicknames, self)
                if self.gameStarted and messageSplit[0] != lobby.currPlayer.name:
                    client.sendall("It's not your turn yet, please wait.".encode())
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
            self.nicknames.append(nickname)
            self.clients.append(client)
            print(f"Nickname of the client is {nickname}")
            self.broadcast(f"{nickname} joined the lobby!")
            thread = threading.Thread(target=self.handle, args=(client,))
            thread.start()


if __name__ == "__main__":
    Server()
