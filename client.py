#Jesus Ugarte
# University of Central Florida
# Chat Client

import socket 
import threading 

stop_thread = False

while True:
    host = input('Enter ip address to connect\n') #ethernet
    try:
        socket.inet_aton(host)
        break
    except socket.error:
        print('Invalid IP')
                    
print(f'Connected to: {host}')

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, 50842))

nickname = input("Choose a nickname: ")
if nickname == 'admin':
    password = input("Enter password for admin: ")


def receive():
    while True:
        global stop_thread
        if stop_thread:
            break
        try:
            message = client.recv(1024).decode('utf-8')

            if message == 'NICK':
                client.send(nickname.encode('utf-8'))
                next_message = client.recv(1024).decode('utf-8')
                if next_message == 'PASS':
                    client.send(password.encode('utf-8'))
                    if client.recv(1024).decode('utf-8') == 'REFUSE':
                        print("Connection was  refused! Wrong Password!")
                        stop_thread = True
                elif next_message == 'BAN':
                    print('Connection refused because of ban!')
                    client.close()
                    stop_thread = True
            elif message == 'EXIT':
                print('Sucessful exit!')
                client.close()
                stop_thread = True
            elif message == 'KILL':
                print('Admin decided to shut down Service')
                client.close()
                stop_thread = True
            else:
                print(message)

        except:
            print("An error ocurred!")
            client.close()
            break

def write():
    while True:
        if stop_thread:
            break

        message = f'{nickname}: {input("")}'

        #Know if a command is trying to be executed
        if message[len(nickname)+2:].startswith('/'):
            #handle exit situation
            if message[len(nickname)+2:].startswith('/exit'):
                client.send(f'EXIT'.encode('utf-8'))
                break
            #Handle username commands
            elif nickname == 'admin':
                if message[len(nickname)+2:].startswith('/kick'):
                    client.send(f'KICK {message[len(nickname)+2+6:]}'.encode('utf-8'))
                elif message[len(nickname)+2:].startswith('/ban'):
                    client.send(f'BAN {message[len(nickname)+2+5:]}'.encode('utf-8'))
                if message[len(nickname)+2:].startswith('/kill'):
                    client.send(('KILL').encode('utf-8'))
                    break
            else:
                print("Commands can only be executed by the admin!")
        else:
            client.send(message.encode('utf-8'))

receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()