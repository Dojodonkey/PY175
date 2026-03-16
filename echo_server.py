import socket

'''
A TCP server.
AF_INET: Specifies address family (IPv4) for the Internet Protocol.
SOCK_STREAM: Indicates use of a TCP socket for data streams.
'''
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Tell the server where to listen for requests, binding the server to an address.
server_socket.bind(('localhost', 3003))
server_socket.listen()

print("Server is running on localhost:3003")
# Now the server will listen for incoming connections on specified address.

'''
But we want the server to run on an infinite loop, constantly listening for new connections.
The `accept` method waits for a connection from the client and when received returns a tuple, the first value being a new socket object representing the connection and the second is the address of the client.
'''
while True:
    client_socket, addr = server_socket.accept()
    print(f"Connection from {addr}")
    # So we are listening, accepting and capturing information about the connection now.
    # To read the incoming data:
    # within our `while` loop
    request = client_socket.recv(1024).decode()
    # `recv` method reads data from client. `1024` is the buffer size, telling `recv` to read 1024 bytes of data at a time.
    # `decode` method converts those bytes to a string as data is transmitted in bytes.
    '''
    Browser often automatically request a sites favicon (little icon in the tab) or send empty requests. We will skip these to prevent errors.
    '''
    # within our `while` loop
    if (not request) or ('favicon.ico' in request):
        client_socket.close()
        continue
    # Lastly we want to grab the first line of a request, construct a response and send #it.
    # within our `while` loop
    request_line = request.splitlines()[0]
    response = ("HTTP/1.1 200 OK\r\n"
                "Content-Type: text/plain\r\n"
                f"Content-Length: {len(request_line)}\r\n"
                "\r\n"
                f"{request_line}\n")

    client_socket.sendall(response.encode())
    client_socket.close()
    # Some browsers expect a well formed response to be rendered.
    # Note we've determined the `Content-Length` value.
    # `encode` converts the response string to bytes.
    # `sendall` sends the response to the client.
    # `close` then closes that connection concluding handling one client's request.
