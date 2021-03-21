# bot.py
import os
import random

import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents.default()
intents.members = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    guild = discord.utils.get(client.guilds, name=GUILD)
    print('Mafia de Cuba bot is up.')


# Global game variables
opened = False
started = False
numberOfPlayers = 0
players = {}
box = {}
playersOrder = []
godfather = ''

def constructBox(context, name):
    global box, numberOfPlayers

    boxString = ''

    if context == 'start':
        boxString += f'This is the box for a {numberOfPlayers} people game: \n\n'
    elif context == 'pass':
        boxString += f'Take the box {name}. Don\' show it to anyone or Tony Hawkings will kill you.\n\n'
    boxString += '----------------- \n'
    boxString += f'Loyals - {box["loyals"]} \n'
    boxString += f'Agents - {box["agents"]} \n'

    if 'taxidrivers' in box:
        boxString += f'Taxidrivers - {box["taxidrivers"]} \n'

    boxString += f'Diamonds - {box["diamonds"]} \n'
    boxString += '----------------- \n\n'

    if 'jokers' in box:
        boxString += f'The Godfather has {box["jokers"]} Jokers. \n\n'
    else:
        boxString += "The Godfather has no Jokers!"

    return boxString


def constructTable(currentPlayer):
    global numberOfPlayers, playersOrder

    tableString = 'Table: :wrestling:\n'

    for i in range(numberOfPlayers):
        if playersOrder[i] == currentPlayer:
            tableString += '(' + str(i+1) + ') **' + playersOrder[i] + '** :briefcase:\n'
        else:
            tableString += '(' + str(i+1) + ') ' + playersOrder[i] + '\n'
    
    tableString += '\n Godfather: ' + godfather + ' :ring:\n'


@client.event
async def on_message(message):
    global opened, started, players, numberOfPlayers, box

    # Opening game session
    if message.content == '!mafia open':
        if (not opened):
            opened = True
            await message.channel.send(
                ':dagger: Buenas noches hijos de puta! :dagger:\n\n'
                ':arrow_right: Use `!mafia join` to join the session.\n'
                ':arrow_right: Use `!mafia leave` to leave the session.\n'
                ':arrow_right: Use `!mafia start` to start the game when all players have joined the session.\n'
                ':arrow_right: Use `!mafia godfather` if you want to be the godfather.\n\n'
                ':gem: To start the game you need 5 to 12 players in the session.'
            )
        else:
            await message.channel.send(
                f'{message.author.name} is a Tony Hawking. The game is already opened...'
            )

    # Player joining
    elif message.content == '!mafia join':
        if opened and (not started) and (message.author.name not in players.keys()):
            players[message.author.name] = 'TBD'
            playerList = '\n - '.join(players.keys())
            await message.channel.send(
                f'{message.author.name} joined the game! :gun:\nPlayers in the room **[{len(players)}]**:\n - {playerList}'
            )
        elif message.author.name in players.keys():
            await message.channel.send(
                f'{message.author.name} is a Tony Hawking. You are already in the room...'
            )
        elif started:
            await message.dm_channel.send(
                f'Sorry {message.author.name}, but the game has already started. Wait until it ends and you can join the next one!'
            )

    # Player leaving
    elif message.content == "!mafia leave":
        if opened and (not started):
            if message.author.name in players.keys():
                players.pop(message.author.name)
                playerList = '\n - '.join(players.keys())
                await message.channel.send(
                    f'{message.author.name} left the game! What a pussy.\nPlayers in the room **[{len(players)}]**:\n - {playerList}'
                )

    # Game starting
    elif message.content == "!mafia start":
        if opened:
            numberOfPlayers = len(players)
            if numberOfPlayers < 5 or numberOfPlayers > 12:
                await message.channel.send('The number of players must be between 5 and 12!')
            else:
                started = True

                if numberOfPlayers == 5:
                    box = {'loyals':1, 'agents':1, 'diamonds':15}
                elif numberOfPlayers == 6:
                    box = {'loyals':1, 'agents':1, 'taxidrivers':1, 'diamonds':15}
                elif numberOfPlayers == 7:
                    box = {'loyals':2, 'agents':1, 'taxidrivers':1, 'diamonds':15}
                elif numberOfPlayers == 8:
                    box = {'loyals':3, 'agents':1, 'taxidrivers':1, 'jokers':1, 'diamonds':15}
                elif numberOfPlayers == 9:
                    box = {'loyals':4, 'agents':1, 'taxidrivers':1, 'jokers':1, 'diamonds':15}
                elif numberOfPlayers == 10:
                    box = {'loyals':4, 'agents':2, 'taxidrivers':1, 'jokers':1, 'diamonds':15}
                elif numberOfPlayers == 11:
                    box = {'loyals':4, 'agents':2, 'taxidrivers':2, 'jokers':2, 'diamonds':15}
                else:
                    box = {'loyals':5, 'agents':2, 'taxidrivers':2, 'jokers':2, 'diamonds':15}

                for player in players.keys():
                    if players['player'] != 'godfather':
                        playersOrder.append(player)

                random.shuffle(playersOrder)

                tableString = constructTable(playersOrder[0])

                boxString = constructBox('start', message.author.name)
                await message.channel.send(tableString + boxString)

        elif (not opened):
            await message.channel.send(
                'First you need to open a room with "!mafia open".\n'
                'In case you need help use "!mafia help".'
            )
    
    # Godfather selected
    elif message.content == "!mafia godfather":
        if opened and (not started):
            players[message.author.name] = 'godfather'
            godfather = message.author.name
            await message.channel.send(f'{message.author.name} is the Godfather! :ring:')

client.run(TOKEN)
