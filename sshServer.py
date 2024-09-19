import paramiko
import socket
import threading
import base64
import time

class SSHServer(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()
        self.allowed_keys = self.load_allowed_keys()

    def load_allowed_keys(self):
        allowed_keys = []
        with open('public.key', 'r') as f:
            for line in f:
                key_data = base64.b64decode(line.split()[1].encode())
                allowed_keys.append(paramiko.RSAKey(data=key_data))
        return allowed_keys

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        if username == 'admin' and password == 'password':
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def check_auth_publickey(self, username, key):
        if username == 'admin' and key in self.allowed_keys:
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

def handle_client(client, server_instance):
    try:
        transport = paramiko.Transport(client)
        transport.add_server_key(paramiko.RSAKey(filename='private.key'))
        transport.start_server(server=server_instance)

        chan = transport.accept(5)  # Channel timeout set to 5 seconds
        if chan is None:
            print("No channel.")
            return

        chan.send("Welcome to the SSH server!\n")  # Send welcome message immediately
        keep_alive_interval = 2  # Keep-alive interval set to 2 seconds

        while True:
            try:
                message = chan.recv(1024).decode('utf-8').strip()
                if message.lower() == 'exit':
                    chan.send("Goodbye!\n")
                    break
                print(f"Received message: {message}")
                chan.send(f"Received message: {message}\n")

                # Send keep-alive message
                chan.send("\0")
                time.sleep(keep_alive_interval)  # Send keep-alive every 2 seconds
            except Exception as e:
                print(f"Exception: {e}")
                break

        chan.close()
        transport.close()
    except Exception as e:
        print(f"Exception in handle_client: {e}")
    finally:
        client.close()

def start_server():
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('0.0.0.0', 2222))  # Ensure the server listens on port 2222
        server_socket.listen(5)
        print("Server started and listening for connections...")

        while True:
            try:
                client, addr = server_socket.accept()
                print(f"Connection from {addr}")
                threading.Thread(target=handle_client, args=(client, SSHServer())).start()
            except socket.error as e:
                print(f"Socket error: {e}")
                break
    except Exception as e:
        print(f"Exception in start_server: {e}")
    finally:
        server_socket.close()
        print("Server socket closed.")

if __name__ == "__main__":
    start_server()