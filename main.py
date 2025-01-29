import socket
from struct import pack, unpack
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
    filler = P1InputPtr + 0x10  # 0x8 in length, read array of bytes here
    leftStickHorizontal = P1InputPtr + 0x18  # s8
    leftStickVertical = P1InputPtr + 0x19  # s8
    filler2 = P1InputPtr + 0x1B  # 0x2 in length
    rightStickHorizontal = P1InputPtr + 0x1C  # s8
    rightStickVertical = P1InputPtr + 0x1D  # s8
    port = P1InputPtr + 0x1E  # u8
    filler3 = P1InputPtr + 0x1F  # 0x5 in length
    initStatus2 = P1InputPtr + 0x24  # u32, seems to be time since last new input not held down actually...
    initStatus = P1InputPtr + 0x28  # bool
    unk29 = P1InputPtr + 0x29  # bool
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
    # message = input('Type a sentence to send\n')
    newInputTimer = dolphin_memory_engine.read_word(PlayerInput.timeSinceLastInput.value)

    if newInputTimer == 0:
        # TODO: add full controller struct data transfer
        # Input = {
        #     "timeSinceLastInput": dolphin_memory_engine.read_word(newInputTimer),
        #     "unk4": dolphin_memory_engine.read_word(PlayerInput.unk4.value),
        #     "holdFaceButtons": dolphin_memory_engine.read_word(PlayerInput.holdFaceButtons.value),
        #     "toggleFaceButtons": dolphin_memory_engine.read_word(PlayerInput.toggleFaceButtons.value),
        #     "filler": dolphin_memory_engine.read_bytes(PlayerInput.filler.value, 0x8),
        #     "leftStickHorizontal": dolphin_memory_engine.read_byte(PlayerInput.leftStickHorizontal.value),
        #     "leftStickVertical": dolphin_memory_engine.read_byte(PlayerInput.leftStickHorizontal.value),
        #     "filler2": dolphin_memory_engine.read_bytes(PlayerInput.filler2.value, 0x2),
        #     "rightStickHorizontal": dolphin_memory_engine.read_byte(PlayerInput.rightStickHorizontal.value),
        #     "rightStickVertical": dolphin_memory_engine.read_byte(PlayerInput.rightStickVertical.value),
        #     "port": dolphin_memory_engine.read_byte(PlayerInput.port.value),
        #     "filler3": dolphin_memory_engine.read_bytes(PlayerInput.filler3.value, 0x5),
        #     "initStatus2": dolphin_memory_engine.read_word(PlayerInput.initStatus2.value),
        #     "initStatus": dolphin_memory_engine.read_byte(PlayerInput.initStatus.value),
        #     "unk29": dolphin_memory_engine.read_byte(PlayerInput.unk29.value),
        #     "filler4": dolphin_memory_engine.read_bytes(PlayerInput.filler4.value, 0x6)
        # }
        #
        # inputFormatString = f"!4Lp2bp2bBpL2?p"  #
        # message = pack(inputFormatString,
        #                Input["timeSinceLastInput"],
        #                Input["unk4"],
        #                Input["holdFaceButtons"],
        #                Input["toggleFaceButtons"],
        #                Input["filler"],
        #                Input["leftStickHorizontal"],
        #                Input["leftStickVertical"],
        #                Input["filler2"],
        #                Input["rightStickHorizontal"],
        #                Input["rightStickVertical"],
        #                Input["port"],
        #                Input["filler3"],
        #                Input["initStatus2"],
        #                Input["initStatus"],
        #                Input["unk29"],
        #                Input["filler4"])

        message = (dolphin_memory_engine.read_word(PlayerInput.holdFaceButtons.value))
        tcpClientSocket.send(message.to_bytes(2, 'big'))
        modifiedMessage = tcpClientSocket.recv(2048)
        print("Sent inputs: ", hex(int.from_bytes(modifiedMessage, byteorder='big')))
    pass


if __name__ == '__main__':
    startDolphinHook()
    opponentSearch()
    client = connectPlayers()
    # syncPlayers(client)
    while True:
        sendAndReceive(client)
    # ServerTest.ServerLoop()
