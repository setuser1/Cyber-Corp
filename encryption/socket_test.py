# first of all import the socket library 
import socket as s
import random
import algo

def generate_key():
    # Generate a random key for encryption/decryption
    key = random.randint(500, 1000)  # Insecurely small, just for demo
    return key

privkey = generate_key()

global pubkey
global other_pubkey
global mixkey  # Declare mixkey as a global variable
other_pubkey = None
mixkey = None  # Initialize mixkey

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

def keyexchange(pubkey=None, other_pubkey=None, privkey=None, prime=397):
    # Compute the shared secret
    shared_secret = pow(other_pubkey, privkey, prime)*pubkey*1837732
    print(f"Shared secret: {shared_secret}")
    return shared_secret

s = s.socket(s.AF_INET, s.SOCK_STREAM)
pubkey = pubkey()

def server_mode():
    global other_pubkey, mixkey
    s.bind(('0.0.0.0', port))
    s.listen(5)
    print(f"Server listening on port {port}...")
    c, addr = s.accept()
    print(f"Connected to {addr}")

    # Send the server's public key
    c.send(str(pubkey).encode())
    print(f"Public key sent: {pubkey}")

    # Receive the client's public key
    other_pubkey = int(s.recv(1024).decode())
    print(f"Public key received: {other_pubkey}")

    # Perform key exchange
    mixkey = keyexchange(pubkey, other_pubkey, privkey, 397)
    print(f"Shared secret: {mixkey}")

    return mixkey,c

def client_mode():
    global other_pubkey, mixkey
    server_ip = input("Enter the server IP: ")
    try:
        s.connect((server_ip, port))
        print(f"Connected to server {server_ip}:{port}")
    except Exception as e:
        print(f"Connection failed: {e}")
        return None

    # Receive the server's public key
    other_pubkey = int(s.recv(1024).decode())
    print(f"Public key received: {other_pubkey}")

    # Send the client's public key
    s.send(str(pubkey).encode())
    print(f"Public key sent: {pubkey}")

    # Perform key exchange
    mixkey = keyexchange(pubkey, other_pubkey, privkey, 397)
    print(f"Shared secret: {mixkey}")

    return mixkey,s

def system(mode):
    if mode == 'server':
        mixkey,conn = server_mode()
    elif mode == 'client':
        mixkey,conn = client_mode()
    else:
        print("Invalid mode selected.")
        return

    if conn:
        print('Connection established.')
        print('Shared secret:', mixkey)
        print('Public key:', other_pubkey)
        print('Connection: ', conn)

        
        # Encrypt the message using the shared key
        
        while True:
            options = str(input("Encrypt or Decrypt? (e/d/x): "))
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
            elif options.lower() == 'x':
                print("Exiting...")
                break
        return mixkey

def send(conn, message):
    # send the message to the user
    conn.send(message.encode())
    print('Message sent:', message)

def main():
    mode = input("Enter mode (server/client): ").strip().lower()
    mixkey = system(mode)

mixkey = main()

if __name__ == "__main__":
    main()
