from queue import Queue
from blitz import blitzStrike
import numpy as np
from geopy import distance

class proximityMath:
    def __init__(self, locLat: float, locLong: float, notifyDistance: float, strikeQueue: Queue, discordQueue: Queue):
        self.loc = np.array([locLat, locLong])
        self.strikeQueue = strikeQueue
        self.notifyDistance = notifyDistance
        self.discordQueue = discordQueue

    '''
    Proximity checker begins watching Strike queue and calcs the distances
    '''
    def start(self):
        #TODO: this will be happening in a thread so need a way to exit
        while True:
            item = self.strikeQueue.get()
            if type(item) == blitzStrike:
                strike = item
                #calc lat long distance in miles
                distance_miles = distance.distance(self.loc, strike.loc).miles
                #compare to distance handed in
                if distance_miles <= self.notifyDistance:
                    strike.distFromUser = distance_miles
                    #send to discord queue
                    self.discordQueue.put(blitzStrike)

def proxyStart(locLat: float, locLong: float, notifyDistance: float, strikeQueue: Queue, discordQueue: Queue):
    #bermuda 'home'
    #32.38569, -64.781278
    a = proximityMath(locLat=locLat, locLong=locLong, notifyDistance=notifyDistance, strikeQueue=strikeQueue, discordQueue=discordQueue)
    a.start()


if __name__ == "__main__":
    from time import sleep
    import threading

    strikeQueue = Queue()
    discordQueue = Queue()

    proxyThread = threading.Thread(target=proxyStart, kwargs={"locLat":32.38569, "locLong":-64.781278, "notifyDistance":5, "strikeQueue":strikeQueue, "discordQueue":discordQueue}, daemon=True)
    proxyThread.start()

    sleep(4)

    #should hit near
    strikeQueue.put(blitzStrike({"time": 123456789, 
                             "lat": 32.38560, 
                             "lon": -64.781278, 
                             "alt": 0,
                             "pol": 0,
                             "mds": 2.3,
                             "mcg": 5.43,
                             "sig": [],
                             "region": 2,
                             "delay": 5.34,
                             "lonc": 0,
                             "latc": 0
                            }
                        )
                )
    sleep(1)
    #should not hit near
    strikeQueue.put(blitzStrike({"time": 123456789, 
                             "lat": 30.38560, 
                             "lon": -64.781278, 
                             "alt": 0,
                             "pol": 0,
                             "mds": 2.3,
                             "mcg": 5.43,
                             "sig": [],
                             "region": 2,
                             "delay": 5.34,
                             "lonc": 0,
                             "latc": 0
                            }
                        )
                )
