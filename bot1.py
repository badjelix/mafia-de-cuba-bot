# bot.py
import os
import random

import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_BOT1_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents.default()
intents.members = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    guild = discord.utils.get(client.guilds, name=GUILD)
    await guild.text_channels[1].send('!mafia join')
    print('Bot1 is up.')

# @client.event
# async def on_message(message):
#     if message == '!bot1 join':
#         await message.channel.send('!mafia join')

client.run(TOKEN)
