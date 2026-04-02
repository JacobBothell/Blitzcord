from websockets.sync.client import connect, ClientConnection
import json
import logging
from queue import Queue
import threading

class blitzStrike:
    def __init__(self, rawBlitzDict: dict):
        self.time = rawBlitzDict['time']
        self.lat = rawBlitzDict['lat']
        self.long = rawBlitzDict['lon']
        self.altitude = rawBlitzDict['alt']
        self.pol = rawBlitzDict['pol'] #polarity?
        self.mds = rawBlitzDict['mds'] #maximal deviation span in nano seconds
        self.mcg = rawBlitzDict['mcg'] #maximal circular gap in degrees
        if 'status' in rawBlitzDict:
            self.status = rawBlitzDict['status'] #optional
        self.sig = rawBlitzDict['sig'] #array of signals associated with this strike
        self.region = rawBlitzDict['region']
        self.delay = rawBlitzDict['delay']
        self.lonc = rawBlitzDict['lonc']
        self.latc = rawBlitzDict['latc']

class blitz:
    def __init__(self, dataQueue: Queue):
        self.logger = logging.getLogger("Blitz_Interface")
        self.dataQueue = dataQueue

    '''
    Establish connection with Blitzortung via ws and emit processed json objects
    '''
    def listen(self):
        #connection to blitz
        #TODO: add multiple attempts to different servers
        self.logger.info("Connecting to Blitzortung")
        #TODO: add some protection here if the ws closes on us
        with connect("wss://ws1.blitzortung.org/") as ws:
            if self.informBlitz(ws):
                while ws:
                    msg = ws.recv()
                    self.dataQueue.put(blitzStrike(self.decodeBlitz(msg)))
                    #print(msg)
        #print data
        #on message process json and insert into queue
    
    '''
    Send opening information to Bliz about what info we would like to recieve

    returns success or failure of sending opening data
    '''
    def informBlitz(self, ws: ClientConnection) -> bool:
        opener = {'a':111}
        try:
            ws.send(json.dumps(opener))
            return True
        except Exception as e:
            self.logger.error(e)
            return False
        
    '''
    Decode JSON data sent by Blitz into object
    '''
    def decodeBlitz(self, rawMsg: str) -> blitzStrike:
        try:
            encodeChar1 = rawMsg[0]
            encodeChar2 = rawMsg[0]
            encodeCharDict = {}
            dictIndex = 256
            deobfStr = rawMsg[0]
            for aChar in rawMsg[1:]:
                charA = ord(aChar)
                if charA >= 256:
                    if charA in encodeCharDict:
                        aChar = encodeCharDict[charA]
                    else:
                        aChar = encodeChar1 + encodeChar2
                deobfStr += aChar
                encodeChar1 = aChar[0]
                encodeCharDict[dictIndex] = encodeChar2 + encodeChar1
                dictIndex += 1
                encodeChar2 = aChar
            return json.loads(deobfStr)
        except Exception as e:
            self.logger.error(e)
            return None
        
    def processRawLocation(self, rawMsg):
        pass

def startBlitz(dataQueue: Queue):
    a = blitz(dataQueue)
    a.listen()

if __name__ == "__main__":
    logging.basicConfig(level=logging.NOTSET)

    q = Queue()
    blitzThread = threading.Thread(target = startBlitz, kwargs={"dataQueue":q}, daemon=True)
    blitzThread.start()

    a = 0
    while a < 5:
        item = q.get()
        print(type(item))
        print(item)
        a += 1

#TODO: blitz string for testing later
#{"time":17751552ĉ5769Ĉ200,"latĆ37.50ď42ęlonĆď.63ĥ84ęalĝ:Ę"polĆĸmdsĆ14ĒĲ"mcgī31ęstĜuŁķęregiĩłŎiŊ:[Āŏaŋ56ęĂĄłď3ģņěĶ35.2860ČħŚ:24.ğ94ťĳĵĞŷŎŐtŒŪ},šŐī907ŧăąć432ƙƓĚĜĞ8.4408įŹĪŻ2.88268ō"ĴĶČƜŢƉœ12ƌƎţŻ6ƢƔũćĮƀżħƞ:ğ.03ư93Ƨīƪ1ŃċƱƳƐƇőƹƻƍ"ŢīŶ8ǂƖĈ6ǨǎǈĶ41ĭ9Ģ19ǒŻŽ73921ŦƲƄć74ǳǠƈƊćǞƽīȀƜŨǦ7806ĊǫĆƣ.Ċ62șǴƚ.13ƯńƃƴŶǛƸƋǟǡǵ9ȋƕłƬǨĢȓ:ĥȝŴƥǤĚźż.ǐēƯȢł65ȥȅƺƼȃƾżƑǥł998ǰȸůȔƪƁƭ2ɃȹƨȻǐ7ČȂǙȳǺɄǝɇȩŃĮɌŻŷįƘȲǋȀ5ƀȂĨɛ0ƫğĢǑǽƴȂƷɅȇɈȉĒɪșǲȁĦƝǬɕȽǍț3žɳŴɀć18ƶȄɥȨƏǊǺɻȌǢƯƤɴǉȴʗď5ɻɵīǮɲǨʄɼĞȤɈȦǄɦʜżıɪƙčŵŮʥ6ųǸŌəʫŻĠȑƚ7ɠǾưɤȧȈʝƮʻť5ńƱɓǊƠŃʧŮźČġĈȎʔǐˏǵʷɉǨņʠǊǰČƣȲ4ˁȞƚĈǴǲĭ˲ˋˌƴƦʴȅ4˨Ȯ8əˬƣǀˋĸ˙ƁžŬƒ˞ƨĈȖȐʰɡǺəɿœ́ʛƾˢȬǃ̇˖ƙ˱˳ˋƥǼˆ˸ŷ1ǍȸɡǕ̘ʙȔ̂ƩǀɪƣĔĖɒʥǮ0ȁē˷ŽűȎʗʔʰ̙̳̜ȉƺ̷2ȫ3ȟ˱Žȶğ̨˟ŲƢ˖ɣʱʕ˦̛ˑŴɩāȭȳ˲ȟċ˱ƪǎʹ˘˟ʐŌǀ͢ɡƯʘǜːʂ:ȏǼ̆˗ń˅̼ơǀǹ̐ŪƫǰĖʉɡ͐˦̴̬ż0Ȃͼɗď˱ƠʩıͭɛǮƁĊ9ǼΊ7ʉ͈ȳ̴ʖŃ̷Ģƚƥ˱ĠΐʧΙłĠƑģ̣͜șȸΣ͟͸ˋ̟ƖƁǨɘʪ΀ȏˋƁ˷ƪǹĊ5̮ǾȟɻΣʁɧτ̷ĉƣğΕƫǍ͐Ɯ̩9ĭğȎəɡċĸιΎȀʉ̆ϡɬ˱ϞƒƺˣɚīɷďǨ˥͜Ưɾ̲Τ͊Ǌ˯̷ı˖φʊȔϞπȐțǮē4̄ϢǾƮθϻǻΥĔ̅ͤЌ̢ȁ̤Ȗ7̏ΰć͘Ƣʗ˼Ğ͇ϻκɧ˻Ѐč̰ϘϚȿϲǿžΘͨ͜ƺņϦϽǹϩЗʾűʉ̋ϞɳϰțƪģıΞʔɘ΢ϻϑʸȁƱ̆ʧƑͿǬĠČǸ˷Ų̄ǍȑʔǸǼй͠˲ͻнıų̛ʥƠƤƢŸб̒ďǺƚʔȞ̱ͶϼˑɨνȔɐΡЈЄȳїğĖʪ͗ơĎ6͌ϸ˰˿̚Υʯ̷ƀȐĔϘČȐŌ˷έȑ̀жаѢ͸ǹʟЗǰȀȏȲĢǌē̬҅ΚȼΡ͎ΟЏʖ˦юƾȎѻȳΞǷɎ͒ȝЌǺ͖̑ɕɲđΉǾ-ҌϐΥŵЖ̠ΞƬ΋ҀńųȎҡњġșɭʔɂБѷШʜŬǰґēӡάȝŬǭҬłŲŴƑЌʔʈΌ6ΥНѥӎΡƁʤǬʐǕŶщѯǮŵǻӯζӿҟɧƀҸȁ̹Ҍ̋ŲĒȏʓѯʐǀӀɻɡҼҍ͉̈́͠ɪǱǍǕ˱ʐƘĖƂԀƫɐƙФŻɐ͞ҏǁͣǃɺűɏЮɲǲӪǄžǺˢѴŵԮ]ędeěyȔƧcĽǫՉķ}
    