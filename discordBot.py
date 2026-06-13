import discord
import logging
import asyncio
from datetime import datetime, timezone, timedelta
import math

from proximityMath import proximityLocation

class BlitzcordBot(discord.Client):
    def __init__(self, *, intents, **options):
        super().__init__(intents=intents, **options)

        self.logger = logging.getLogger("Blitzcord_Discord")
        self.notification_channels = []

        self.guild_notifications = {}
        self.notification_cooldown = int(options['cool_down'])
        #self.loop = options['loop']

    async def on_ready(self):
        self.loop = asyncio.get_running_loop()
        self.logger.info(f'Logged on as {self.user}')

        await self.get_lightning_channels()
        
    
    async def get_lightning_channels(self):
        self.logger.info("Looking for Lightning channel")
        for guild in self.guilds:
            l_chan = await self.get_create_guild_lightning_channel(guild)

            if type(l_chan) == discord.TextChannel:
                self.notification_channels.append(l_chan)

        await self.get_last_notify()

    async def get_last_notify(self):
        for chan in self.notification_channels:
            #fill with default value
            self.guild_notifications[chan.guild.name] = datetime.now(timezone.utc) - timedelta(days=1)
            async for msg in chan.history(limit=50):
                if msg.author.id == self.user.id:
                    self.guild_notifications[chan.guild.name] = msg.created_at
                    break

    async def get_create_guild_lightning_channel(self, guild: discord.Guild) -> None | discord.TextChannel: 
        lightning_channels = [chan for chan in guild.text_channels if chan.name=="lightning"]
        if len(lightning_channels) > 0:
            if len(lightning_channels) > 1:
                self.logger.error(f'Multiple lightning channels found for guild {guild.name}. Situation is ambiguous!')
                return None
            else:
                self.logger.info(f'Found lightning channel for guild {guild.name}')
                return lightning_channels[0]
        else:
            self.logger.info(f'No lightning channel found for guild {guild.name}. Adding channel')

            try:
                create_return = await guild.create_text_channel("lightning")
            except Exception as e:
                self.logger.error(f'Error when creating channel in guild {guild.name}. {e}')

            if type(create_return) == discord.TextChannel:
                return create_return
            else:
                self.logger.error(f'Could not create lightning channel for guild {guild.name}')

    async def notify_of_strike(self, guild_strikes: list[proximityLocation]):
        if self.is_ready():
            #pre-compute guilds we would notify
            known_guilds = [c.guild.name for c in self.notification_channels]
            chan_iter = map(lambda strike: (self.notification_channels[known_guilds.index(strike.name)], strike), guild_strikes)

            for chan, strike in chan_iter:
                #if cooldown has expired make a new post
                if chan.guild.name in self.guild_notifications and (datetime.now(timezone.utc) - self.guild_notifications[chan.guild.name]).seconds >= self.notification_cooldown*60:
                    await chan.send(f'<t:{math.floor(datetime.now().timestamp())}>   Lightning strike within {math.floor(strike.lastNotifyStrikeDistance)} miles')
                #if it has not expired update the last post
                else:
                    async for msg in chan.history(limit=10):
                        if msg.author.id == self.user.id:
                            #quick little math that keeps the closest one and slowly allows it to move away
                            #example content  '<t:1780982042>   Lightning strike within 48 miles'
                            msg_distance = int(msg.content.split(" ")[-2])
                            if msg.edited_at:
                                msg_time = msg.edited_at
                            else:
                                msg_time = msg.created_at
                            time_diff = (datetime.now(timezone.utc) - msg_time).seconds / 60
                            dst_growth = msg_distance*(math.e**(0.05*time_diff))
                            if math.floor(strike.lastNotifyStrikeDistance) < msg_distance or (math.floor(strike.lastNotifyStrikeDistance) > msg_distance and math.floor(strike.lastNotifyStrikeDistance) < dst_growth):
                                await msg.edit(content=f'<t:{math.floor(datetime.now().timestamp())}>   Lightning strike within {math.floor(strike.lastNotifyStrikeDistance)} miles')
                                percent_change = (msg_distance-math.floor(strike.lastNotifyStrikeDistance)) / msg_distance
                                #add reaction if strike comes 30% closer
                                if percent_change > 0.3 and percent_change > 0:
                                    await msg.add_reaction("⚡")
                                    strike.reactionCounter += 1
                                #remove it after a few strikes so we can use that notification again
                                if strike.reactionCounter >= 5:
                                    await msg.remove_reaction("⚡", self.user.id)
                            break

                self.guild_notifications[chan.guild.name] = datetime.now(timezone.utc)
    
    def notify_of_strike_wrapper(self, guild_strikes: list[proximityLocation]):
        if self.is_ready():
            asyncio.run_coroutine_threadsafe(self.notify_of_strike(guild_strikes), self.loop)

def run_bot_in_thread(client: discord.Client, token: str, loop):
    asyncio.set_event_loop(loop)

    async def start_client():
        await client.start(token)
    
    loop.create_task(start_client())
    loop.run_forever()

#testing apparatus
async def testBotNotify(bot: BlitzcordBot, testing_server, loop):
    await asyncio.sleep(3)
    asyncio.run_coroutine_threadsafe(bot.notify_of_strike([proximityLocation('testingBlitzcord', '90','90','3')]), loop)

if __name__ == "__main__":
    from dotenv import dotenv_values
    from threading import Thread

    dotValues = dotenv_values(".env")
    discord_secret = dotValues['DISCORD_SECRET']

    intents = discord.Intents.default()
    intents.message_content = True

    loop = asyncio.new_event_loop()

    client = BlitzcordBot(intents=intents, cool_down=10)#, loop=loop)

    discordThread = Thread(target=run_bot_in_thread, args=(client, discord_secret, loop), daemon=True)
    discordThread.start()

    asyncio.run(testBotNotify(client, dotValues['DISCORD_TESTING_SERVER'], loop))