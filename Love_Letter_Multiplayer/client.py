import socket
import threading

nickname = input("Please enter a nickname: ")
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("25.14.115.139", 21011))  # lan ip of host
print("You have connected to the server")


def receive():
    while True:
        try:
            message = client.recv(1024).decode()
            print(message)

        except:
            print("An error occurred!")
            client.close()
            break


def write():
    client.sendall(nickname.encode())
    while True:
        message = f"{nickname}: {input("")}"
        client.sendall(message.encode())


receive_thread = threading.Thread(target=receive)
receive_thread.start()

receive_thread = threading.Thread(target=write)
receive_thread.start()

if __name__ == "__main__":
    pass
