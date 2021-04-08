#Jesus Ugarte
# University of Central Florida
# Chat Server

import socket
import threading 
import requests


host = '0.0.0.0' #ethernet
address = requests.get('https://api.ipify.org/').text
print(f'current host address is: {address}')

port = 50842

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

clients =[]
nicknames =[]

#Broadcast to all users
def broadcast(message):
    message = message.decode('ascii')
    message = f'{message}\n'.encode('ascii')
    #Broadcasting msg to all clients
    for client in clients:
        client.send(message)

def kick_user(name):
    if name in nicknames:
        name_index = nicknames.index(name)
        client_to_kick = clients[name_index]
        clients.remove(client_to_kick)
        client_to_kick.send('You were kicked by admin!'.encode('ascii'))
        client_to_kick.close()
        nicknames.remove(name)
        broadcast(f'{name} was kicked by an admin'.encode('ascii'))
        print(f'{name} was kicked by the admin')

def handle(client):
    #Handling disconnection username exceptions
    while True:
        try:
            msg = message = client.recv(1024)

            #Handle exit situation
            if msg.decode('utf-8').startswith('EXIT'):
                client.send('EXIT'.encode('ascii'))
                client_to_exit = nicknames[clients.index(client)]
                for client in clients:
                    client.send(f'{client_to_exit} left the chat')

            #handle command instructions 
            elif msg.decode('utf-8').startswith('KICK'):
                if nicknames[clients.index(client)] == 'admin':
                    name_to_kick = msg.decode('utf-8')[5:]
                    kick_user(name_to_kick)
                else: #Making sure server is not exploited
                    client.send('Command was refused!'.encode('ascii'))
            #ban command
            elif msg.decode('utf-8').startswith('BAN'):
                if nicknames[clients.index(client)] == 'admin':
                    name_to_ban = msg.decode('utf-8'[4:])
                    kick_user(name_to_ban)
                    with open('bans.txt', 'a') as f:
                        f.write(f'{name_to_ban}\n')
                    print(f'{name_to_ban} was banned!')
                else:#Making sure server is not exploited
                    client.send('Command was refused!'.encode('ascii'))
            #kill command
            elif msg.decode('utf-8').startswith('KILL'):
                if nicknames[clients.index(client)] == 'admin':
                    for client in clients:
                        client.send('KILL'.encode('ascii'))
                        print(f'{nicknames[clients.index(client)]} left the chat')
                else:
                    client.send('Command was refused!'.encode('ascii'))

            else:
                broadcast(message)

        except:
            if client in clients:
                index = clients.index(client)
                clients.remove(client)
                client.close()
                nickname = nicknames[index]
                broadcast(f'{nickname} left the chat!'.encode('ascii'))
                nicknames.remove(nickname)
                break

def receive():
    while True:

        #Accept the new connection
        client, address = server.accept()
        print(f"Connected with {str(address)}")

        #Signal requesting username
        client.send('NICK'.encode('ascii'))

        nickname = client.recv(1024).decode('ascii')

        with open('bans.txt', 'r') as f:
            bans = f.readlines()

        if nickname+'\n' in bans:
            client.send('BAN'.encode('ascii'))
            client.close()
            continue

        #Checking for admin priviledge
        if nickname =='admin':
            client.send('PASS'.encode('ascii'))
            password = client.recv(1024).decode('ascii')

            #NOT SECURE WAY TO CHECK FOR PASSWORD
            if password != 'adminpass':
                client.send('REFUSE'.encode('ascii'))
                client.close()
                continue

        nicknames.append(nickname)
        clients.append(client)
        
        #Broadcasting all the membes that a member has joined 
        print(f"Nickname of the client is {nickname}!")
        broadcast(f'{nickname} joined the chat!'.encode('ascii'))
        client.send("Connected to the server!".encode('ascii'))
        
        #Start threading using handle function
        thread = threading.Thread(target=handle , args = (client,))
        thread.start()

print("Server is listening...")
receive()