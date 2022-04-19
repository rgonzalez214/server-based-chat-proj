import socket

HOST_IP = "127.0.0.1"
PORT = 8008

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((HOST_IP, PORT))

while True:
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    print("received message: %s" % data)

    # Send back to data & addr sender, a reply, based on parsing it

    # 1. Check if client is on list of subscribers
    # 2. Retrieve the client’s secret key and send a CHALLENGE (rand) message to the client, using UDP
    # 3. Wait for RESPONSE from client.
    # 4.1 If authentication is not successful, the server sends an AUTH_FAIL message to the client.
    # 4.2 Else generate an encryption key CK-A, then sends an AUTH_SUCCESS(rand_cookie, port_number) message to the client. The message is encrypted by CK-A.
    # From this point on, all data exchanged between client A and the server is encrypted using CK-A.
    # 5. Wait for TCP connection request from client.
    # From this point on, until the TCP connection is closed, all data (signaling messages and chat) is exchanged over the TCP connection.
    # 6. The server sends CONNECTED to the client. The client is connected.
    # 7. If client types “Log off” or when the activity timer expires, the TCP connection is closed.
