import socket
import threading
import pickle
from game import GameInstance

nickname = input("Please enter a nickname: ")
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("25.14.115.139", 21011))  # lan ip of host
print("You have connected to the server")
gameInstance: GameInstance


def receive():
    while True:
        try:
            data = client.recv(1024 * 99)
            global gameInstance
            gameInstance = pickle.loads(data)
            # data = client.sendall(pickle.dumps(data))
            print(gameInstance.alivePlayerCount)
        except:
            print("An error occurred!")
            client.close()
            break


def write():
    client.sendall(nickname.encode())
    while True:
        # message = f"{nickname}: {input("")}"
        message = input("Send command to server: ")
        client.sendall(message.encode())


receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()

if __name__ == "__main__":
    pass
