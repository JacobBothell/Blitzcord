# Blitzcord
This bot works with the (Blitzortung)[https://www.blitzortung.org/] api for its raw lightning data, and posts notification information to a discord channel #lightning.

## Lightning Notifications
Blitzcord will create a post in a #lightning channel whenever a strike is detected in the configured distance (miles) to the configured location (lat/long).

Example Post
'''
June 9, 2026 00:52   Lightning strike within 29 miles
'''

The bot will update that post along with a timestamp whenever a strike comes closer or as the storm moves away. A ⚡ reaction will be added if the strike comes 30% or more closer in order to notify users of fast moving changes. This reaction will be cleared after 10 strikes have been processed in that area so as to allow for future notifications in the future.

There is a configurable cooldown period for the bot creating new posts. This serves to indicate to the bot when it should make a new post vs updating the current one. If strikes continue to be sensed in the detection area the bot will simply update the existing post, but if the cool down timer has expired between strikes then it will make a new post.

### Lightning movement calculation
Strikes that are closer to the configured location are updated immediately and forgo the following algorithm.

Strikes further away than the most recently posted one are evaluated based on time since last strike and relative distance from target location. When a strike happens a circle is created around the target area of that distance; an exponential growth function is used to slowly widen that radius that will be considered for updating the distance.

## Configuring
There are two files that must be edited for the bot.

### .env
There is an `ex.env` that must be changed to `.env` and contain your relavent information
- LOCATIONS_JSON
  - json file has information of the servers and notification settings
- DISCORD_SECRET
  - Secret copied from the discord developers site for this bot
- DISCORD_COOLDOWN
  - Cool down period to determine if a new post should be made or the bot should update existing

### LOCATIONS_JSON
This file is a list of servers / locations that will be monitored by the bot.

Each entry needs the following info:
- name
  - name of discord server
- lat
  - latitude of location to monitor
- long
  - longitude of location to monitor
- notifyDistance
  - radius around the provided lat/long to consider for strikes