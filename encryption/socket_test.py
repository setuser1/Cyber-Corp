# first of all import the socket library 
import socket as s
import random

def generate_key():
    # Generate a random key for encryption/decryption
    key = random.randint(500, 1000)  # Insecurely small, just for demo
    return key

privkey = generate_key()

global pubkey
global other_pubkey
other_pubkey = None

def pubkey():
    # Generate a public key using a random number
    # Shared values (agreed ahead of time)
    prime = 397  # Insecurely small, just for demo
    base = 30

    # Your private key and public key
    pubkey = pow(base, privkey, prime)
    print(f'Your Public key: {pubkey}')
    return pubkey

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

s = s.socket(s.AF_INET, s.SOCK_STREAM)
pubkey = pubkey()

def server_mode():
    global other_pubkey
    s.bind(('0.0.0.0', port))
    s.listen(5)
    print(f"Server listening on port {port}...")
    c, addr = s.accept()
    print(f"Connected to {addr}")

    # Receive the client's public key
    other_pubkey = c.recv(1024).decode()
    print(f"Public key received: {other_pubkey}")

    # Send the server's public key
    c.send(str(pubkey).encode())
    print(f"Public key sent: {pubkey}")

    # Perform key exchange
    mixkey = keyexchange(c, pubkey, int(other_pubkey), privkey, 397)
    print(f"Shared secret: {mixkey}")

    return c, mixkey

def client_mode():
    global other_pubkey
    server_ip = input("Enter the server IP: ")
    try:
        s.connect((server_ip, port))
        print(f"Connected to server {server_ip}:{port}")
    except Exception as e:
        print(f"Connection failed: {e}")
        return None, None

    # Send the client's public key
    s.send(str(pubkey).encode())
    print(f"Public key sent: {pubkey}")

    # Receive the server's public key
    other_pubkey = s.recv(1024).decode()
    print(f"Public key received: {other_pubkey}")

    # Perform key exchange
    mixkey = keyexchange(s, pubkey, int(other_pubkey), privkey, 397)
    print(f"Shared secret: {mixkey}")

    return s, mixkey

def system(mode):
    if mode == 'server':
        conn, mixkey = server_mode()
    elif mode == 'client':
        conn, mixkey = client_mode()
    else:
        print("Invalid mode selected.")
        return

    if conn:
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
                send(conn, encrypted_message)
            elif options.lower() == 'd':
                print("Decrypting...")
                # Decrypt the message using the shared key
                received_message = conn.recv(1024).decode()
                if not received_message:
                    print('No message received. Exiting...')
                    continue
                try:
                    decrypted_message = algo.decode(received_message)     
                except Exception as e:
                    print(f"Error decrypting message: {e}")
                    continue
                print("Message received:", received_message)
                print('Message decrypted:', decrypted_message)

def send(conn, message):
    # send the message to the user
    conn.send(message.encode())
    print('Message sent:', message)

def main():
    mode = input("Enter mode (server/client): ").strip().lower()
    system(mode)

main()
