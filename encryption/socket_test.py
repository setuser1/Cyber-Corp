# first of all import the socket library 
import socket as s

s = s.socket(s.AF_INET, s.SOCK_STREAM)

def init():
    host,user,capab = input("Enter (host,user and capability): ")
    port = 90
    s.bind(('0.0.0.0', port))
    s.listen(5)
    s.accept()


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
