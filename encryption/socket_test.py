# first of all import the socket library 
import socket
import random

def generate_key():
    # Generate a random key for encryption/decryption
    key = random.randint(500, 1000)  # Insecurely small, just for demo
    return key

privkey = generate_key()

global pubkey

def pubkey():
    # Generate a public key using a random number
    # Shared values (agreed ahead of time)
    prime = 397  # Insecurely small, just for demo
    base = 30

    # Your private key and public key
    pubkey = pow(base, privkey, prime)
    print(f'Your Public key: {pubkey}')
    return pubkey

# Declare other_pubkey as a global variable
global other_pubkey
other_pubkey = None

port = 90

def keyexchange(c=None, pubkey=None, other_pubkey=None, privkey=None, prime=397):
    try:
        if c:
            # Send your public key to the peer
            c.send(str(pubkey).encode())
            # Receive the peer's public key
    except ValueError:
        print("Invalid input. Please enter a valid integer.")
        return None, None

    # Compute the shared secret
    shared_secret = pow(other_pubkey, privkey, prime) * 182887372681

    return shared_secret

# Original socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Client socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Third socket for additional purposes
third_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

pubkey = pubkey()

def init():
    global other_pubkey  # Declare it as global to modify the global variable
    # Host and connect first
    host = input("Enter your user: ")
    user = input("Enter the user: ")

    # Bind and listen with the server socket
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen(1)  # Allow 1 connection in the backlog
    print(f"Server listening on port {port}...")

    # Connect with the client socket
    try:
        client_socket.connect((user, port))
        print(f"Connected to {user}:{port}")
    except Exception as e:
        print(f"Connection failed: {e}")
        return None, None, None, 500

    # Accept a connection with the server socket
    c, addr = server_socket.accept()
    print(f"Connected to {addr}")

    # Receive the peer's public key first
    other_pubkey = c.recv(1024).decode()  # Assign to the global variable
    print(f"Public key received: {other_pubkey}")

    # Send your public key to the peer
    c.send(str(pubkey).encode())
    print(f"Public key sent: {pubkey}")

    # Perform key exchange
    mixkey = keyexchange(c, pubkey, int(other_pubkey), privkey, 397)
    print(f"Shared secret: {mixkey}")
    status = 200 if addr else 500

    return host, user, status, mixkey

def system():
    host, user, status, mixkey = init()
    if status == 200:
        print('Connected to the user:', user)
        print('Host:', host)
        print('Status:', status)
        print('Connection established.')
        print('Shared secret:', mixkey)
        print('Public key:', other_pubkey)

        import algo
        # Encrypt the message using the shared key
        while True:
            options = str(input("Encrypt or Decrypt? (e/d): "))
            if options.lower() == 'e':
                unencrypted_message = str(input("Enter the message to encrypt: "))
                encrypted_message = algo.encode(unencrypted_message)
                send(encrypted_message)
            elif options.lower() == 'd':
                print("Decrypting...")
                # Decrypt the message using the shared key
                recieved_message = s.recv(1024).decode()
                if not recieved_message:
                    print('No message received. Exiting...')
                    continue
                try:
                    decrypted_message = algo.decode(recieved_message)     
                except Exception as e:
                    print(f"Error decrypting message: {e}")
                    continue
                print("Message received:", recieved_message)
                print('Message decrypted:', decrypted_message)

def send(message):
    # send the message to the user
    client_socket.send(message.encode())
    print('Message sent:', message)

def main():
    system()

main()
