from socket import *

serverPort = 3601
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen(1)
while True:
    isConnected = True
    conSock, addr = serverSocket.accept()
    print('Riders Online Network is ready to receive inputs from: ', addr)
    while isConnected:
        message = conSock.recv(2048)
        if not message:
            isConnected = False
            conSock.close()
        else:
            # modifiedMessage = message.decode().upper()  # prints uppercase response
            modifiedMessage = int.from_bytes(message, byteorder='big')  # receive guest player's inputs
            print("Received inputs: ", hex(modifiedMessage))
            conSock.send(modifiedMessage.to_bytes(2, 'big'))  # send back our own // .encode()
            # TODO: set up localhost test to write player 2's inputs to dolphin mem engine.
