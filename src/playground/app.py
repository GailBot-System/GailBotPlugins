import socket
import threading
import sys
import time

clients = dict()

def handle_client(me):
    while True:
        try:
            data = clients[me]["client_socket"].recv(1024)
            if not data:
                break
            print(f"Received: {data}")
            not_sent = 0
            while (not_sent < 5):
                try:
                    clients[me + 1]["client_socket"].send(data)
                    not_sent = 5
                except Exception as e:
                    print("bad", e)
                    not_sent += 1
                    time.sleep(0.5)
                    sys.stdout.flush()
            print("sent")
            sys.stdout.flush()

        except ConnectionResetError:
            break
    clients[me]["client_socket"].close()
    # clients.remove(me)

def start_host_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('plugin_0', 9990))
    print("Host server is listening on port 9990...")
    num_clients = 0
    while True:
        print("listening")
        sys.stdout.flush()
        server_socket.listen(5)
 
        print("attempting connection")
        client_socket, client_address = server_socket.accept()
        print(f"Connection from {client_address}")
        clients[num_clients] = {"client_socket": client_socket, "data": ""}
        client_handler = threading.Thread(target=handle_client, args=(num_clients,))
        client_handler.start()
        num_clients += 1

    

if __name__ == "__main__":
    print("started")
    start_host_server()