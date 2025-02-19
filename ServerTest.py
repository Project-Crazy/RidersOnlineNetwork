from socket import *
from struct import pack, unpack
import vgamepad as vg
import time
serverPort = 3601
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen(1)
while True:
    isConnected = True
    conSock, addr = serverSocket.accept()
    print('Riders Online Network is ready to receive inputs from: ', addr)
    gamepad = vg.VX360Gamepad()
    gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
    gamepad.update()
    gamepad.reset()
    while isConnected:
        message = conSock.recv(2048)
        if not message:
            isConnected = False
            conSock.close()
        else:
            # modifiedMessage = message.decode().upper()  # prints uppercase response

            # Unpack the entire struct for inputs, store it, then write the new controller state using vgamepad
            # THIS SHOULD BE 30 BYTES IN LENGTH (0-47 = 48, or 0x30)
            Input = {
                "timeSinceLastInput": unpack('!L', message[:4])[0],  # u32
                "unk4": unpack('!L', message[4:8])[0],  # u32
                "holdFaceButtons": unpack('!L', message[8:12])[0],  # u32
                "toggleFaceButtons": unpack('!L', message[12:16])[0],  # u32
                "tapPulseFaceButtons": unpack('!L', message[16:20])[0],  # u32
                "holdPulseFaceButtons": unpack('!L', message[20:24])[0],  # u32
                "leftStickHorizontal": unpack('!b', message[24:25])[0],  # s8
                "leftStickVertical": unpack('!b', message[25:26])[0],  # s8
                "leftTriggerAnalog": unpack('!B', message[26:27])[0],  # u8
                "rightTriggerAnalog": unpack('!B', message[27:28])[0],  # u8
                "rightStickHorizontal": unpack('!b', message[28:29])[0],  # s8
                "rightStickVertical": unpack('!b', message[29:30])[0],  # s8
                "port": unpack('!B', message[30:31])[0],  # u8, maybe u16?
                "collisionFlag1": unpack('!H', message[31:33])[0],  # u16
                "collisionFlag2": unpack('!H', message[33:35])[0],  # u16
                "initStatus2": unpack('!L', message[35:39])[0],  # u32
                "initStatus": unpack('!?', message[39:40])[0],  # bool
                "pauseStatus": unpack('!?', message[40:41])[0],  # bool
                "filler4": unpack('6p', message[41:47])[0]  # unknown...
            }

            gamepad.reset()

            # The vgamepad state should be repeated until new inputs are received (which this loop allows us to do).
            Input['leftStickHorizontal'] = (Input['leftStickHorizontal'] << 8)
            Input['leftStickVertical'] = (Input['leftStickVertical'] << 8)
            Input['rightStickHorizontal'] = (Input['rightStickHorizontal'] << 8)
            Input['rightStickVertical'] = (Input['rightStickVertical'] << 8)

            gamepad.left_joystick(x_value=Input["leftStickHorizontal"], y_value=Input["leftStickVertical"])
            gamepad.right_joystick(x_value=Input["rightStickHorizontal"], y_value=Input["rightStickVertical"])

            # buttonCheck = {
            #
            # }
            # gamepad.press_button(button=vg.XUSB_BUTTON.)

            gamepad.update()

            modifiedMessage = Input["holdFaceButtons"]  # receive guest player's inputs
            print("Received inputs: ", hex(modifiedMessage))
            conSock.send(modifiedMessage.to_bytes(2, 'big'))  # send back our own // .encode()
