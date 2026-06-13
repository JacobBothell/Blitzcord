import threading
from queue import Queue
from dotenv import dotenv_values
import os
import numpy as np
import json
import logging

import asyncio
from threading import Thread
from typing import Callable
import discord

import blitz
import proximityMath
import discordBot

def loadJsonLocations(filename: str) -> list[proximityMath.proximityLocation]:
    if not os.path.isfile(filename):
        raise Exception("Location file not found")
    
    with open(filename, 'r') as file:
        data = json.load(file)

    #letting internal python errors handle this one
    return [proximityMath.proximityLocation(**loc) for loc in data]

def setupDiscordCall(secret, cooldown) -> tuple[Thread, Callable]:
    intents = discord.Intents.default()
    intents.message_content = True

    loop = asyncio.new_event_loop()

    client = discordBot.BlitzcordBot(intents=intents, cool_down=cooldown)

    discordThread = Thread(target = discordBot.run_bot_in_thread, args=(client, secret, loop), name="Discord_Bot", daemon=True)
    discordThread.start()

    return (discordThread, client.notify_of_strike_wrapper)

if __name__ == "__main__":
    dotValues = dotenv_values("./config/.env")

    locations = loadJsonLocations(dotValues['LOCATIONS_JSON'])

    logging.basicConfig(level=logging.INFO, format='%(relativeCreated)6d %(threadName)s %(message)s')

    strikeQueue = Queue()

    discordThread, discordCallback = setupDiscordCall(dotValues['DISCORD_SECRET'], dotValues['DISCORD_COOLDOWN'])
    BlitzThread = threading.Thread(target=blitz.startBlitz, kwargs={"dataQueue":strikeQueue}, name="Blitzortung_Interface", daemon=True)
    ProxyQueue = threading.Thread(target=proximityMath.proxyStart, kwargs={"locations":locations, "strikeQueue":strikeQueue, "callbacks":[discordCallback]}, name="Proxy_Math", daemon=True)

    BlitzThread.start()
    ProxyQueue.start()

    threads = [discordThread,BlitzThread,ProxyQueue]

    for thread in threads:
        thread.join()