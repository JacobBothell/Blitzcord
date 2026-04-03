import blitz
import proximityMath
import threading
from queue import Queue
from dotenv import dotenv_values
import os




if __name__ == "__main__":
    dotValues = dotenv_values(".env")

    strikeQueue = Queue()
    discordQueue = Queue()

    BlitzThread = threading.Thread(target=blitz.startBlitz, kwargs={"dataQueue":strikeQueue}, daemon=True)
    #TODO: replace location info from .evn file
    ProxyQueue = threading.Thread(target=proximityMath.proxyStart, kwargs={"locLat":float(dotValues['LOCLAT']), "locLong":float(dotValues['LOCLONG']), "notifyDistance":float(dotValues['NOTIFYDISTANCT']), "strikeQueue":strikeQueue, "discordQueue":discordQueue}, daemon=True)


    BlitzThread.start()
    ProxyQueue.start()

    while True:
        item = discordQueue.get()
        if type(item) == blitz.blitzStrike:
            print(f'distance: {item.distFromUser}')