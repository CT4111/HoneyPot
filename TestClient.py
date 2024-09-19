import time

import paramiko

# Define connection parameters
hostname = '127.0.0.1'
port = 2222  # Ensure the client connects to port 2222
username = 'admin'
private_key_file = 'path/to/private.key'

# Create SSH client
ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    # Load private key
    private_key = paramiko.RSAKey(filename=private_key_file)

    # Connect to the server using the private key
    ssh_client.connect(hostname, port, username, pkey=private_key)

    # Open a session
    session = ssh_client.get_transport().open_session()
    if session.active:
        print(session.recv(1024).decode('utf-8'))
        while True:
            # Read user input
            command = input("Enter command: ")
            # Send the command
            session.send(command)
            # Receive and print the response
            print(session.recv(1024).decode('utf-8'))
            # Exit loop if the command is 'exit'
            if command.lower() == 'exit':
                break

finally:
    # Close the connection
    ssh_client.close()
