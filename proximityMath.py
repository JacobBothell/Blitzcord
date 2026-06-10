from queue import Queue
from blitz import blitzStrike
import numpy as np
import numpy.typing as npt
from geopy import distance
from typing import Callable

class proximityLocation():
    def __init__(self, name: str, lat: float, long: float, notifyDistance: float):
        self.name = name
        self.lat = lat
        self.long = long
        self.notifyDistance = notifyDistance
        #below used by the discord bot
        self.strikeDistance = None
        self.reactionCounter = 0
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
                strike = item
                #calc lat long distances in miles
                for loc in self.locations:
                    loc.setStrikeDistance(distance.distance(loc.loc, strike.loc).miles)
                #compare to distance in object
                places_needing_notify = [loc for loc in self.locations if loc.notifyDistance >= loc.strikeDistance]
                if len(places_needing_notify) > 0:
                    for call in self.callbacks:
                        call(places_needing_notify)


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
