import socket
import random


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
    # Organize display of headers:
    method, path_params, version = request_line.split()
    path, params = path_params.split('?')
    params = params.split('&')
    params_dict = {}
    for param in params:
        key, value = param.split('=')
        params_dict[key] = value
    rolls = int(params_dict.get('rolls', 1))
    sides = int(params_dict.get('sides', 6))

    # Updated Response body:
    response_body = ("<html><head><title>Dice Rolls</title></head><body>"
                     f"<h1>HTTP Request Info:</h1>"
                     f"<p><strong>Request Line</strong>: {request_line}</p>"
                     f"<p><strong>HTTP Method</strong>: {method}</p>"
                     f"<p><strong>Path</strong>: {path}</p>"
                     f"<p><strong>Parameters</strong>: {params_dict}</p>"
                     f"<h2>Rolls:</h2>"
                     "<ol>")

    for _ in range(1, rolls+1):
        roll = random.randint(1, sides)
        response_body += f"<li>{roll}</li>"

    response_body += "</ol></body></html>"

    response = ("HTTP/1.1 200 OK\r\n"
                "Content-Type: text/html\r\n"
                f"Content-Length: {len(response_body)}\r\n"
                "\r\n"
                f"{response_body}\n")

    client_socket.sendall(response.encode())
    client_socket.close()
    # Some browsers expect a well formed response to be rendered.
    # Note we've determined the `Content-Length` value.
    # `encode` converts the response string to bytes.
    # `sendall` sends the response to the client.
    # `close` then closes that connection concluding handling one client's request.