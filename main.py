import socket
from struct import pack, unpack
import ctypes
import dolphin_memory_engine
from socket import *
from enum import Enum

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 3601

PlayerPtr = 0x805369a0
PlayerStructLength = 0x1080

dolphin_memory_engine.hook()

P1InputPtr = dolphin_memory_engine.read_word(
    PlayerPtr)  # We can get the controller ptr right at the start since it should not change in gameplay
P2InputPtr = dolphin_memory_engine.read_word(
    PlayerPtr + 0x1080)  # We can get the controller ptr right at the start since it should not change in gameplay


class PlayerInput(Enum):
    timeSinceLastInput = P1InputPtr  # u32
    unk4 = P1InputPtr + 0x4  # u32
    holdFaceButtons = P1InputPtr + 0x8  # u32
    toggleFaceButtons = P1InputPtr + 0xC  # u32
    tapPulseFaceButtons = P1InputPtr + 0x10  # u32, pulses whenever you rapidly input new inputs values (for QTEs?)
    holdPulseFaceButtons = P1InputPtr + 0x14  # u32, pulses whenever you hold values (for QTEs?)
    # filler = P1InputPtr + 0x10  # 0x8 in length, read array of bytes here (REDUNDANT)
    leftStickHorizontal = P1InputPtr + 0x18  # s8
    leftStickVertical = P1InputPtr + 0x19  # s8
    leftTriggerAnalog = P1InputPtr + 0x1A  # u8
    rightTriggerAnalog = P1InputPtr + 0x1B  # u8
    # filler2 = P1InputPtr + 0x1B  # 0x2 in length, byte 1 is L-trigger analog val, byte 2 is R-trigger val (REDUNDANT)
    rightStickHorizontal = P1InputPtr + 0x1C  # s8
    rightStickVertical = P1InputPtr + 0x1D  # s8
    port = P1InputPtr + 0x1E  # u8, might be u16???
    # + 0x1F goes unused for now...
    collisionFlag1 = P1InputPtr + 0x20  # u16
    collisionFlag2 = P1InputPtr + 0x22  # u16
    # filler3 = P1InputPtr + 0x1F  # 0x5 in length (REDUNDANT)
    initStatus2 = P1InputPtr + 0x24  # u32, seems to be time since last new input not held down actually...
    initStatus = P1InputPtr + 0x28  # bool
    pauseStatus = P1InputPtr + 0x29  # bool
    # unk29 = P1InputPtr + 0x29  # bool (REDUNDANT)
    filler4 = P1InputPtr + 0x2A  # 0x6 in length
    pass


# First, start by hooking dolphin
def startDolphinHook():
    spinlock = False  # just so we don't keep repeating the same message. Goofy check.
    while not dolphin_memory_engine.is_hooked():
        if not spinlock:
            print("Dolphin not connected, waiting for an instance to be opened...")
        spinlock = True

    print("Dolphin connected. Starting opponent search.")
    pass


# Then, search for opponents
def opponentSearch():
    pass


# After an opponent is found, create a connection
def connectPlayers():
    # Create a TCP socket. We know it's a TCP socket because we use SOCK_STREAM.
    tcpClientSocket = socket(AF_INET, SOCK_STREAM)
    # Connect the socket to a server listening at the specified network address. Note that the connect function
    # accepts a single parameter (a tuple containing the network address), not two separate parameters.
    tcpClientSocket.connect((SERVER_HOST, SERVER_PORT))
    return tcpClientSocket


# Once connection is created, sync inputs, player structs, and RNG seed
def syncPlayers(tcpClientSocket):
    pass


# Keep updating these as needed according to desyncs and player states
def sendAndReceive(tcpClientSocket):
    # Take inputs from one player, send to another

    """
    THIS FUNCTION IS EXTREMELY IMPORTANT, So I'll explain the what, how, and why.

    This function will send a packet of input data (read from the game's memory) and send it to the server.
    The server will receive this, and then replicate these inputs on the other player's dolphin instance,
    UNTIL A NEW PACKET IS SENT.

    This means that, if a packet of inputs is sent, the other player's "opponent" will keep repeating the input until
    a new packet is sent.

    This packet is ONLY SENT when the input state changes.
    This ENTIRELY DEPENDS ON THE "timeSinceLastInput" value from the game itself being equal to 0.
    The value resets to zero when:
    A new button has been pressed.
    A button has been released.
    A new joystick input has been recognized.

    EX. If the player holds down the A button, one packet will be sent and the action will be continued until
    the timer is set to zero.

    EX.2. If the player drifts a corner and maintains the exact inputs that they used to drift the corner with,
    the actions will keep the player drifting until it is finished.

    What should happen is that we have less requests and reads to do from the server, and then since the player's
    inputs are only required when a new one is sent due to being able to preserve the state of their last input,
    we can ensure that inputs should not drop unless not received at all at a point. At that point, that is a desync,
    which we can handle elsewhere.
    """

    newInputTimer = dolphin_memory_engine.read_word(PlayerInput.timeSinceLastInput.value)

    if newInputTimer == 0:
        Input = {
            "timeSinceLastInput": dolphin_memory_engine.read_word(newInputTimer),  # L
            "unk4": dolphin_memory_engine.read_word(PlayerInput.unk4.value),  # L
            "holdFaceButtons": dolphin_memory_engine.read_word(PlayerInput.holdFaceButtons.value),  # L
            "toggleFaceButtons": dolphin_memory_engine.read_word(PlayerInput.toggleFaceButtons.value),  # L
            "tapPulseFaceButtons": dolphin_memory_engine.read_word(PlayerInput.tapPulseFaceButtons.value),  # L
            "holdPulseFaceButtons": dolphin_memory_engine.read_word(PlayerInput.holdPulseFaceButtons.value),  # L
            # "filler": dolphin_memory_engine.read_bytes(PlayerInput.filler.value, 0x8),  # values found, see notes
            "leftStickHorizontal": dolphin_memory_engine.read_byte(PlayerInput.leftStickHorizontal.value),  # b
            "leftStickVertical": dolphin_memory_engine.read_byte(PlayerInput.leftStickVertical.value),  # b
            "leftTriggerAnalog": dolphin_memory_engine.read_byte(PlayerInput.leftTriggerAnalog.value),  # B
            "rightTriggerAnalog": dolphin_memory_engine.read_byte(PlayerInput.rightTriggerAnalog.value),  # B
            # "filler2": dolphin_memory_engine.read_bytes(PlayerInput.filler2.value, 0x2),  # values found, see notes
            "rightStickHorizontal": dolphin_memory_engine.read_byte(PlayerInput.rightStickHorizontal.value),  # b
            "rightStickVertical": dolphin_memory_engine.read_byte(PlayerInput.rightStickVertical.value),  # b
            "port": dolphin_memory_engine.read_byte(PlayerInput.port.value),  # B, but probs H?
            "collisionFlag1": int.from_bytes(dolphin_memory_engine.read_bytes(PlayerInput.collisionFlag1.value, 0x2), byteorder='big'),  # H
            "collisionFlag2": int.from_bytes(dolphin_memory_engine.read_bytes(PlayerInput.collisionFlag2.value, 0x2), byteorder='big'),  # H
            # "filler3": dolphin_memory_engine.read_bytes(PlayerInput.filler3.value, 0x5),
            "initStatus2": dolphin_memory_engine.read_word(PlayerInput.initStatus2.value),  # L
            "initStatus": dolphin_memory_engine.read_byte(PlayerInput.initStatus.value),  # ?
            "pauseStatus": dolphin_memory_engine.read_byte(PlayerInput.pauseStatus.value),  # ?
            # "unk29": dolphin_memory_engine.read_byte(PlayerInput.unk29.value),
            "filler4": dolphin_memory_engine.read_bytes(PlayerInput.filler4.value, 0x6)  # 6p
        }

        inputFormatString = f"!6L2b2B2bB2HL2?6p"

        # Fix unsigned to sign because DME package sux :(
        Input['leftStickHorizontal'] = (Input['leftStickHorizontal'] & 0x7f) - 0x80 if Input['leftStickHorizontal'] >= 0x9C else Input['leftStickHorizontal']
        Input['leftStickVertical'] = (Input['leftStickVertical'] & 0x7f) - 0x80 if Input['leftStickVertical'] >= 0x9C else Input['leftStickVertical']
        Input['rightStickHorizontal'] = (Input['rightStickHorizontal'] & 0x7f) - 0x80 if Input['rightStickHorizontal'] >= 0x9C else Input['rightStickHorizontal']
        Input['rightStickVertical'] = (Input['rightStickVertical'] & 0x7f) - 0x80 if Input['rightStickVertical'] >= 0x9C else Input['rightStickVertical']

        # IMPORTANT: THIS ENTIRE MESSAGE SHOULD BE 30 BYTES EVEN.
        message = pack(inputFormatString,
                       Input["timeSinceLastInput"],
                       Input["unk4"],
                       Input["holdFaceButtons"],
                       Input["toggleFaceButtons"],
                       Input["tapPulseFaceButtons"],
                       Input["holdPulseFaceButtons"],
                       Input["leftStickHorizontal"],
                       Input["leftStickVertical"],
                       Input["leftTriggerAnalog"],
                       Input["rightTriggerAnalog"],
                       Input["rightStickHorizontal"],
                       Input["rightStickVertical"],
                       Input["port"],
                       Input["collisionFlag1"],
                       Input["collisionFlag2"],
                       Input["initStatus2"],
                       Input["initStatus"],
                       Input["pauseStatus"],
                       Input["filler4"])

        # message = (dolphin_memory_engine.read_word(PlayerInput.holdFaceButtons.value))  # Old test case protocol
        # tcpClientSocket.send(message.to_bytes(2, 'big'))  # Old test case protocol

        tcpClientSocket.send(message)
        modifiedMessage = tcpClientSocket.recv(2048)  # Should receive input struct, use vgamepad to reflect inputs here
        # For now, we'll just display 'em
        print("Sent inputs: ", hex(int.from_bytes(modifiedMessage, byteorder='big')))

        # print("Sent inputs: ", hex(int.from_bytes(modifiedMessage, byteorder='big')))
    pass


if __name__ == '__main__':
    startDolphinHook()
    opponentSearch()
    client = connectPlayers()
    # syncPlayers(client)
    while True:
        sendAndReceive(client)
    # ServerTest.ServerLoop()
