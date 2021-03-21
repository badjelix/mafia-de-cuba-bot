# game.py
import os
import random

import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
CHANNEL = os.getenv('DISCORD_CHANNEL')
guild = ''

intents = discord.Intents.default()
intents.members = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    global guild, guildChannel
    guild = discord.utils.get(client.guilds, name=GUILD)
    for channel in guild.channels:
        if channel.name == CHANNEL:
            guildChannel = channel

    print('Mafia de Cuba bot is up.')


# Global game variables
opened = False
started = False
godfatherSelect = False
numberOfPlayers = 0
players = {}
box = {}
playersOrder = []
godfather = ''


def constructBox(context, name):
    global box, numberOfPlayers

    boxString = ''

    if context == 'start':
        boxString += '**Box:**\n\n'
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
    global numberOfPlayers, playersOrder, godfather

    tableString = '**Table:**\n'

    for i in range(numberOfPlayers-1):
        if playersOrder[i] == currentPlayer:
            tableString += '(' + str(i+1) + ') **' + playersOrder[i] + '** :briefcase:\n'
        else:
            tableString += '(' + str(i+1) + ') ' + playersOrder[i] + '\n'
    
    if godfather == currentPlayer:
        tableString += '\n **Godfather**: ' + godfather + ' :ring: :briefcase:\n\n'
    else:
        tableString += '\n **Godfather**: ' + godfather + ' :ring:\n\n'

    return tableString


@client.event
async def on_message(message):
    global guild, guildChannel, opened, started, players, numberOfPlayers, box, godfather, godfatherSelect


    # Opening game session
    if message.content == '!mafia open':
        if not opened:
            opened = True
            await guildChannel.send(
                ':dagger: Buenas noches hijos de puta! :dagger:\n\n'
                ':arrow_right: Use `!mafia join` to join the session.\n'
                ':arrow_right: Use `!mafia leave` to leave the session.\n'
                ':arrow_right: Use `!mafia start` to start the game when all players have joined the session.\n'
                ':arrow_right: Use `!mafia godfather` if you want to be the godfather.\n\n'
                ':gem: To start the game you need 5 to 12 players in the session.'
            )
        else:
            await guildChannel.send(
                f'{message.author.name} is a Tony Hawking. The game is already opened...'
            )


    # Player joining
    elif message.content == '!mafia join':
        if opened and (not started) and (message.author.name not in players.keys()):
            players[message.author.name] = 'TBD'
            playerList = '\n - '.join(players.keys())
            await guildChannel.send(
                f'{message.author.name} joined the game! :gun:\nPlayers in the room **[{len(players)}]**:\n - {playerList}'
            )
        elif message.author.name in players.keys():
            await guildChannel.send(
                f'{message.author.name} is a Tony Hawking. You are already in the room...'
            )
        elif started:
            await guildChannel.send(
                f'Sorry {message.author.name}, but the game has already started. Wait until it ends and you can join the next one!'
            )


    # Player leaving
    elif message.content == '!mafia leave':
        if opened and (not started):
            if message.author.name in players.keys():
                players.pop(message.author.name)
                playerList = '\n - '.join(players.keys())
                await guildChannel.send(
                    f'{message.author.name} left the game! What a pussy.\nPlayers in the room **[{len(players)}]**:\n - {playerList}'
                )


    # Game starting
    elif message.content == '!mafia start':
        if godfather == '':
            await guildChannel.send('Select the Godfather before starting the game.')
        elif opened:
            numberOfPlayers = len(players)
            if numberOfPlayers < 5 or numberOfPlayers > 12:
                await guildChannel.send('The number of players must be between 5 and 12!')
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
                    if player != godfather:
                        playersOrder.append(player)

                random.shuffle(playersOrder)

                tableString = constructTable(godfather)

                boxString = constructBox('start', message.author.name)

                await guildChannel.send(tableString + boxString)

                godfatherMember = ''
                for member in guild.members:
                    if member.name == godfather:
                        godfatherMember = member

                godfatherSelect = True

                await godfatherMember.create_dm()
                await godfatherMember.dm_channel.send(f'Godfather {godfatherMember.name}, ' +
                                                        'please select how many diamonds you want to remove (from 0-5) from the box. ' +
                                                        'Use the message `!mafia remove <number of diamonds>`\n')
        elif not opened:
            await guildChannel.send(
                'First you need to open a room with "!mafia open".\n'
                'In case you need help use "!mafia help".'
            )
    

    # Godfather selected
    elif message.content == '!mafia godfather':
        if opened and (not started):
            players[message.author.name] = 'godfather'
            godfather = message.author.name
            await guildChannel.send(f'{message.author.name} is the Godfather! :ring:')


    # Godfather removes diamonds from box
    elif message.content[:13] == '!mafia remove':
        if started and godfatherSelect and (message.author.name == godfather) and (int(message.content[14]) <= 5 and int(message.content[14]) >= 0):
            box["diamonds"] = box["diamonds"] - int(message.content[14])
            await guildChannel.send('**The Godfather passed the box!**\n\n' + constructTable(playersOrder[0]))
            godfatherSelect = False
        elif started and godfatherSelect and (message.author.name == godfather) and (int(message.content[14]) > 5 or int(message.content[14]) < 0):
            await message.channel.send('You can only remove from 0 to 5 diamonds.')


client.run(TOKEN)
