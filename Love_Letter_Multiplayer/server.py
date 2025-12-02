import threading
import socket

from lobby import Lobby

host = "0.0.0.0"  # local host
port = 21012

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((host, port))
server.listen()

clients: list[socket.socket] = []
nicknames: list[str] = []


def broadcast(message: str):
    for client in clients:
        client.sendall(message.encode())


def handle(client: socket.socket):
    while True:
        try:
            message: str = client.recv(1024).decode()
            messageSplit: list[str] = message.split(":")
            if messageSplit[1].strip() == "start":
                lobby = Lobby(nicknames)
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            broadcast(f"{nickname} left the lobby")
            nicknames.remove(nickname)
            break


def receive():
    while True:
        client, address = server.accept()
        print(f"Connected with {str(address)}")
        nickname = client.recv(1024).decode()
        nicknames.append(nickname)
        clients.append(client)
        print(f"Nickname of the client is {nickname}")
        broadcast(f"{nickname} joined the lobby!")
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()


print("Server is listening...")
try:
    receive()
finally:
    server.close()
