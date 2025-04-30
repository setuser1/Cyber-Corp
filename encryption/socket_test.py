# first of all import the socket library 
import socket as s

s = s.socket(s.AF_INET, s.SOCK_STREAM)

def init():
    host = input("Enter your host: ")
    capability = input("Enter your capability (s/r or both(sr)): ")
    recipent = input("Enter the recipent: ")


def system():
    host,capability,recipent = init()
    # bind the socket to the host and port
    s.bind(('0.0.0.0', 90))
    
    s.listen(5)
    print('Listening active')
    # accept connections from outside
    user = input("Enter the ip of user: ")
    conn, addr = s.accept()
    print('Got connection from', addr)
    s.connect((str(user),90))
    
    status = None
    # check if the user is connected to us
    if addr == user:
        print('user connected to us')
        status = 200
    else:
        print('user not connected to us')
        status = 404
    
    # status
    print('Connected to', user)
    if addr == user:
        print('user connected to us')
    s.send(capability.encode())
    # receive the capability of the user
    data = conn.recv(1024).decode()
    print('Recieved capability:', data)
    # check if the capability of user
    if data == 's':
        print('user is a sender')
    elif data == 'r':
        print('user is a receiver')
    elif data == 'sr':
        print('user is a sender and receiver')
        
    print('Recieved capability:', data)
    print('Host:', host)
    print('Recipent:', recipent)
    print('Status:', status)

def send(message):
    # send the message to the user
    while True:
        s.send(message.encode())
        print('Message sent:', message)
        
        if message == 'exitsecret':
            print('Exiting...')
            break
        elif message == 'help':
            print('Available commands: exit, help')

def receive():
    # receive the message from the user
    while True:
        try:
            data = s.recv(1024).decode()
            if not data:  # Check if the connection is closed
                print('Connection closed by the user.')
                break
            print('Message received:', data)
        except ConnectionResetError:
            print('Connection lost.')
            break

def send_recieve():
    # send and receive messages
    while True:
        message = input('Enter your message: ')
        if message == 'exitsecret':
            print('Exiting...')
            break
        elif message == 'help':
            print('Available commands: exit, help')
        else:
            send(message)
            receive()
    

def main():
    None