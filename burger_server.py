import socket, errno

SERVER_ADDR = (HOST, PORT) = '', 3500
QUEUE_SIZE = 1024

def handle_request(conn):
    req = conn.recv(1024)
    print req.decode()

    res = b"""\
            BURGER/0.1 RECEIVED OK

            This is the burger protocol. Wanna some fries?
            """

    conn.sendall(res)

def listen():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(SERVER_ADDR)
    sock.listen(QUEUE_SIZE)

    print 'Serving a bunch of BURGERS on port {port} ...'.format(port=PORT)

    while True:
        conn, addr = sock.accept()
        handle_request(conn)
        conn.close()
