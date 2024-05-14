import socket

host = "localhost"
port = 7777

s = socket.socket()
s.connect((host, port))

# received the banner
data = s.recv(1024)
print(data.decode().strip())

while True:
    user_input = input("").strip()
    s.sendall(user_input.encode())
    reply = s.recv(1024).decode().strip()
    print(reply)
    if "Goodbye" in reply:
        break
    if "Play again" in reply and "yes/no" in reply:
        continue
s.close()
