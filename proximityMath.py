from queue import Queue
from blitz import blitzStrike
import numpy as np
import numpy.typing as npt
import math
from geopy import distance
from typing import Callable
from datetime import datetime, timezone
import logging

class proximityLocation():
    def __init__(self, name: str, lat: float, long: float, notifyDistance: float):
        self.name = name
        self.lat = lat
        self.long = long
        self.notifyDistance = notifyDistance
        #below used by the discord bot
        self.strikeDistance = None
        self.lastNotifyStrikeDistance = notifyDistance
        self.lastNotifyStrikeTime = datetime.now(timezone.utc)
    @property
    def loc(self) -> npt.NDArray[np.float64]:
        '''
        Returns lat, long in numpy array
        '''
        return np.array([self.lat,self.long])
    def setStrikeDistance(self, dist: float):
        '''
        sets object lightning strike distance param and returns object
        '''
        self.strikeDistance = dist
        return self
    def updateLastStrike(self):
        self.lastNotifyStrikeDistance = self.strikeDistance
        self.lastNotifyStrikeTime = datetime.now(timezone.utc)

class proximityMath:
    def __init__(self, locations: list[proximityLocation], strikeQueue: Queue, callbacks: list[Callable]):
        self.locations = locations
        self.strikeQueue = strikeQueue
        self.callbacks = callbacks

    '''
    Proximity checker begins watching Strike queue and calcs the distances
    '''
    def start(self):
        #TODO: this will be happening in a thread so need a way to exit
        while True:
            item = self.strikeQueue.get()
            if type(item) == blitzStrike:
                self.calcDistances(item)

                places_needing_notify = self.getNotifyLocs()

                if len(places_needing_notify) > 0:
                    self.updateNotifyData(places_needing_notify)
                    for call in self.callbacks:
                        call(places_needing_notify)
    def calcDistances(self, strike: blitzStrike):
        #calc lat long distances in miles
        for loc in self.locations:
            loc.setStrikeDistance(distance.distance(loc.loc, strike.loc).miles)
    def getNotifyLocs(self) -> list[proximityLocation]:
        #compare to distance in object
        places_needing_notify = [loc for loc in self.locations if loc.notifyDistance >= loc.strikeDistance]

        #check previous notifications
        #perform dist exponential calc
        if len(places_needing_notify) > 0:
            places_needing_notify = [loc for loc in places_needing_notify if loc.lastNotifyStrikeDistance*(math.e**(0.05*((datetime.now(timezone.utc)-loc.lastNotifyStrikeTime).seconds/60))) > loc.strikeDistance]
            if len(places_needing_notify) > 0:
                logging.info(f'Sending notifications to {[loc.name for loc in places_needing_notify]}')

        return places_needing_notify

    def updateNotifyData(self, locations: list[proximityLocation]) -> None:
        for loc in locations:
            loc.updateLastStrike()
        
def proxyStart(locations: list[proximityLocation], strikeQueue: Queue, callbacks: list[Callable]):
    #bermuda 'home'
    #32.38569, -64.781278
    a = proximityMath(locations, strikeQueue=strikeQueue, callbacks=callbacks)
    a.start()


if __name__ == "__main__":
    from time import sleep
    import threading

    def testing_callback(location: proximityLocation):
        for loc in location:
            print(f'Recieved location {loc.name} with strike distance of {loc.strikeDistance}')

    strikeQueue = Queue()

    proxyThread = threading.Thread(target=proxyStart, kwargs={"locations":[proximityLocation("home",32.38569,-64.781278,5)], "strikeQueue":strikeQueue, "callbacks":[testing_callback]}, daemon=True)
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
