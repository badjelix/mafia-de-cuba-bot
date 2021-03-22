# game.py
import os
import random
import re

import discord
from dotenv import load_dotenv



#########################
# Environment Variables #
#########################

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
CHANNEL = os.getenv('DISCORD_CHANNEL')
guild = ''

intents = discord.Intents.default()
intents.members = True

# Connect client to Discord
client = discord.Client(intents=intents)

# Method that runs when client as fully connected to Discord
@client.event
async def on_ready():
    global guild, guildChannel
    guild = discord.utils.get(client.guilds, name=GUILD)
    for channel in guild.channels:
        if channel.name == CHANNEL:
            guildChannel = channel
    print('Mafia de Cuba bot is up.')



#########################
# Game Global Variables #
#########################

opened = False
started = False
godfatherSelect = False
godfatherKill = False
godfatherMember = ''
numberOfPlayers = 0
players = {}
box = {}
playersOrder = []
godfather = ''
streetUrchin = False
currentPlayer = ''
currentPlayerId = -1



#####################
# Auxiliary Methods #
#####################

# Constructs Box string given a context and a player name
def constructBox(context, name):
    global box, numberOfPlayers

    boxString = ''

    if context == 'start':
        boxString += '**Box:**\n\n'
    elif context == 'pass':
        boxString += f'Take the box {name}. Don\'t show it to anyone or Tony Hawkings will kill you.\n\n'
    elif context == 'guess:':  # Gui - contexto para a caixa qd volta para o godfather
        boxString += f'Godfather {name}! Here\'s your box but someone has stolen your diamonds!\n'
        boxString += 'Get revenge and retrieve them back using `!mafia kill <traitor name>`.'
    boxString += '----------------- \n'
    boxString += f'Loyals - {box["loyals"]} \n'
    boxString += f'Agents - {box["agents"]} \n'

    if 'taxidrivers' in box:
        boxString += f'Taxidrivers - {box["taxidrivers"]} \n'

    boxString += f'Diamonds - {box["diamonds"]} \n'
    boxString += '----------------- \n\n'
    # se calhar por so os jokers se o context for start
    if 'jokers' in box:
        boxString += f'The Godfather has {box["jokers"]} Jokers. \n\n'
    else:
        boxString += "The Godfather has no Jokers!\n"

    return boxString


# Constructs Table string given the current player name
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


# Constructs Options string possibly with the Street Urchin option
def constructOptions(urchin):
    global box
    optionsString = ''

    if 'loyals' in box:
        optionsString += ':arrow_right: Use `!mafia loyal` if you want to be a Loyal.\n'
    if 'agents' in box:
        optionsString += ':arrow_right: Use `!mafia agent` if you want to be an Agent.\n'
    if 'taxidrivers' in box:
        optionsString += ':arrow_right: Use `!mafia taxidriver` if you want to be a Taxidriver.\n'
    if 'diamonds' in box:
        optionsString += ':arrow_right: Use `!mafia steal <number of diamonds>` to be a thief and remove <number of diamonds> diamonds.\n'
    if urchin:
        optionsString += ':arrow_right: Use `!mafia street urchin` to be a street urchin.\n'

    return optionsString


# Checks if player that receives the box should have the option of being a Street Urchin
def checkStreetUrchin():
    global box

    numberOfElements = 0
    streetUrchin = False

    if 'loyals' in box:
        numberOfElements += box["loyals"]
    if 'agents' in box:
        numberOfElements += box["agents"]
    if 'taxidrivers' in box:
        numberOfElements += box["taxidrivers"]
    if 'diamonds' in box:
        numberOfElements += box["diamonds"]

    if (numberOfElements == 0) or (currentPlayerId == numberOfPlayers - 2):
        streetUrchin = True

    return streetUrchin



#####################
# Game Core Methods #
#####################

# Method that handles the different messages the client receives from Discord
@client.event
async def on_message(message):
    global guild, guildChannel, opened, started, players, currentPlayer, currentPlayerId, numberOfPlayers, box, godfather, godfatherSelect, godfatherKill, godfatherMember


    # OPEN GAME SESSION
    if message.content == '!mafia open':
        if not opened:
            opened = True
            await guildChannel.send(
                ':dagger: Buenas noches hijos de puta! :dagger:\n\n'
                ':arrow_right: Use `!mafia join` to join the session.\n'
                ':arrow_right: Use `!mafia leave` to leave the session.\n'
                ':arrow_right: Use `!mafia godfather` if you want to be the godfather.\n'
                ':arrow_right: Use `!mafia start` to start the game when all players have joined the session.\n\n'
                ':gem: To start the game you need 5 to 12 players in the session.'
            )
        else:
            await guildChannel.send(f'{message.author.name} is a Tony Hawking. The game room is already opened...')


    # PLAYER JOINS
    elif message.content == '!mafia join':
        if opened and (not started) and (message.author.name not in players.keys()):
            players[message.author.name] = 'TBD'
            playerList = '\n - '.join(players.keys())
            await guildChannel.send(f'{message.author.name} joined the game! :gun:\n' +
                                    'Players in the room **[{len(players)}]**:\n - {playerList}'
            )
        elif message.author.name in players.keys():
            await guildChannel.send(f'{message.author.name}, you are a Tony Hawking.' +
                                    'You are already in the room...'
            )
        elif started:
            await guildChannel.send(f'Sorry {message.author.name}, but the game has already started.' +
                                    'Wait until it ends and you can join the next one!'
            )


    # PLAYER LEAVES
    elif message.content == '!mafia leave':
        if opened and (not started):
            if message.author.name in players.keys():
                players.pop(message.author.name)
                playerList = '\n - '.join(players.keys())
                await guildChannel.send(f'{message.author.name} left the game! What a pussy.\n' +
                                        'Players in the room **[{len(players)}]**:\n - {playerList}'
                )


    # GAMES STARTS
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
    

    # SOMEONE SELECTS HIMSELF AS GODFATHER
    elif message.content == '!mafia godfather':
        if opened and (not started):
            players[message.author.name] = 'godfather'
            godfather = message.author.name
            await guildChannel.send(f'{message.author.name} is the Godfather! :ring:')


    # GODFATHER REMOVES DIAMONDS FROM THE BOX
    elif message.content[:13] == '!mafia remove':

        messageSplit = message.content.split()

        matches = bool(re.match("^[-+]?\d+$", messageSplit[2]))

        if matches and started and godfatherSelect and (message.author.name == godfather) and (int(messageSplit[2]) <= 5 and int(messageSplit[2]) >= 0):
            box["diamonds"] = box["diamonds"] - int(messageSplit[2])

            godfatherSelect = False
            currentPlayer = playersOrder[0]
            currentPlayerId = 0


            await guildChannel.send('**The Godfather passed the box!**\n\n' + constructTable(currentPlayer))

            playerMember = ''
            for member in guild.members:
                if member.name == currentPlayer:
                    playerMember = member

            await playerMember.create_dm()
            await playerMember.dm_channel.send(constructBox('pass', currentPlayer) + constructOptions(False))

        elif matches and started and godfatherSelect and (message.author.name == godfather) and (int(messageSplit[2]) > 5 or int(messageSplit[2]) < 0):
            await message.channel.send('You can only remove from 0 to 5 diamonds.')
        
        elif not matches:
            await message.channel.send('You piece of shit.')


    # SOMEONE REMOVES LOYAL
    elif message.content == '!mafia loyal':
        if started and (not godfatherSelect):
            if box["loyals"] > 0:
                box["loyals"] = box["loyals"] - 1
                players[message.author.name] = 'loyal'

                message = f'**{currentPlayer} passed the box!**\n\n'
                currentPlayerId += 1
                if currentPlayerId == numberOfPlayers - 1:  # Gui - caixa passou por toda a gente
                    godfatherKill = True
                    await guildChannel.send('**The box has returned to the Godfather!**\n\n' + constructTable(godfather) +
                                            f'\n\n Godfather {godfather}! Someone has stolen your precious diamonds! :ring:\n' +
                                            ':dagger: Hijos de puta, traidores! :dagger:\n' +
                                            'Find out who and "dispose" of them!')

                    await godfatherMember.create_dm()
                    await godfatherMember.dm_channel.send(constructBox('guess', godfather))

                else:
                    currentPlayer = playersOrder[currentPlayerId]
                    message += constructTable(currentPlayer)
                    await guildChannel.send(message)

                    playerMember = ''
                    for member in guild.members:
                        if member.name == currentPlayer:
                            playerMember = member

                    await playerMember.create_dm()
                    await playerMember.dm_channel.send(constructBox('pass', currentPlayer) + constructOptions(checkStreetUrchin()))

            else:
                message.channel.send('Duh.\n')
        elif started and (not godfatherSelect) and (message.author.name != currentPlayer):
            message.channel.send(f'Shut up {message.author.name}.\n')


    # SOMEONE REMOVES AGENT
    elif message.content == '!mafia agent':
        if started and (not godfatherSelect):
            if box["agents"] > 0:
                box["agents"] = box["agents"] - 1
                players[message.author.name] = 'agent'

                message = f'**{currentPlayer} passed the box!**\n\n'
                currentPlayerId += 1
                if currentPlayerId == numberOfPlayers - 1:
                    godfatherKill = True
                    await guildChannel.send('**The box has returned to the Godfather!**\n\n' + constructTable(godfather)
                                            + f'\n\n Godfather {godfather}! Someone has stolen your precious diamonds! :ring: \n'
                                              ':dagger: Hijos de puta traidores! :dagger:\n'
                                              'Find out who and "dispose" of them!')

                    await godfatherMember.create_dm()
                    await godfatherMember.dm_channel.send(constructBox('guess', godfather))

                else:
                    currentPlayer = playersOrder[currentPlayerId]
                    message += constructTable(currentPlayer)
                    await guildChannel.send(message)

                    playerMember = ''
                    for member in guild.members:
                        if member.name == currentPlayer:
                            playerMember = member

                    await playerMember.create_dm()
                    await playerMember.dm_channel.send(constructBox('pass', currentPlayer) + constructOptions(checkStreetUrchin()))

            else:
                message.channel.send('Duh.\n')
        elif started and (not godfatherSelect) and (message.author.name != currentPlayer):
            message.channel.send(f'Shut up {message.author.name}.\n')


    # SOMEONE REMOVES TAXIDRIVER
    elif message.content == '!mafia taxidriver':
        if started and (not godfatherSelect):
            if box["taxidrivers"] > 0:
                box["taxidrivers"] = box["taxidrivers"] - 1
                players[message.author.name] = 'taxidriver'

                message = f'**{currentPlayer} passed the box!**\n\n'
                currentPlayerId += 1
                if currentPlayerId == numberOfPlayers - 1:
                    godfatherKill = True
                    await guildChannel.send('**The box has returned to the Godfather!**\n\n' + constructTable(godfather)
                                            + f'\n\n Godfather {godfather}! Someone has stolen your precious diamonds! :ring: \n'
                                              ':dagger: Hijos de puta traidores! :dagger:\n'
                                              'Find out who and "dispose" of them!')

                    await godfatherMember.create_dm()
                    await godfatherMember.dm_channel.send(constructBox('guess', godfather))

                else:
                    currentPlayer = playersOrder[currentPlayerId]
                    message += constructTable(currentPlayer)
                    await guildChannel.send(message)

                    playerMember = ''
                    for member in guild.members:
                        if member.name == currentPlayer:
                            playerMember = member

                    await playerMember.create_dm()
                    await playerMember.dm_channel.send(constructBox('pass', currentPlayer) + constructOptions(checkStreetUrchin()))

            else:
                message.channel.send('Duh.\n')
        elif started and (not godfatherSelect) and (message.author.name != currentPlayer):
            message.channel.send(f'Shut up {message.author.name}.\n')


    # SOMEONE REMOVES DIAMONDS
    elif message.content[:15] == '!mafia diamonds':
        if started and (not godfatherSelect):
            if box["taxidrivers"] > 0:
                box["taxidrivers"] = box["taxidrivers"] - 1
                players[message.author.name] = 'thief'

                message = f'**{currentPlayer} passed the box!**\n\n'
                currentPlayerId += 1
                if currentPlayerId == numberOfPlayers - 1:
                    godfatherKill = True
                    await guildChannel.send('**The box has returned to the Godfather!**\n\n' + constructTable(godfather)
                                            + f'\n\n Godfather {godfather}! Someone has stolen your precious diamonds! :ring: \n'
                                              ':dagger: Hijos de puta traidores! :dagger:\n'
                                              'Find out who and "dispose" of them!')

                    await godfatherMember.create_dm()
                    await godfatherMember.dm_channel.send(constructBox('guess', godfather))

                else:
                    currentPlayer = playersOrder[currentPlayerId]
                    message += constructTable(currentPlayer)
                    await guildChannel.send(message)

                    playerMember = ''
                    for member in guild.members:
                        if member.name == currentPlayer:
                            playerMember = member

                    await playerMember.create_dm()
                    await playerMember.dm_channel.send(constructBox('pass', currentPlayer) + constructOptions(checkStreetUrchin()))

            else:
                message.channel.send('Duh.\n')
        elif started and (not godfatherSelect) and (message.author.name != currentPlayer):
            message.channel.send(f'Shut up {message.author.name}.\n')


    # SOMEONE PICKS STREET URCHIN
    elif message.content == '!mafia street urchin':
        if started and (not godfatherSelect):
            if checkStreetUrchin():
                players[message.author.name] = 'streetUrchin'

                message = f'**{currentPlayer} passed the box!**\n\n'
                currentPlayerId += 1
                if currentPlayerId == numberOfPlayers - 1:
                    godfatherKill = True
                    await guildChannel.send('**The box has returned to the Godfather!**\n\n' + constructTable(godfather)
                                            + f'\n\n Godfather {godfather}! Someone has stolen your precious diamonds! :ring: \n'
                                              ':dagger: Hijos de puta traidores! :dagger:\n'
                                              'Find out who and "dispose" of them!')

                    await godfatherMember.create_dm()
                    await godfatherMember.dm_channel.send(constructBox('guess', godfather))

                else:
                    currentPlayer = playersOrder[currentPlayerId]
                    message += constructTable(currentPlayer)
                    await guildChannel.send(message)

                    playerMember = ''
                    for member in guild.members:
                        if member.name == currentPlayer:
                            playerMember = member

                    await playerMember.create_dm()
                    await playerMember.dm_channel.send(constructBox('pass', currentPlayer) + constructOptions(True))

            else:
                message.channel.send('Duh.\n')
        elif started and (not godfatherSelect) and (message.author.name != currentPlayer):
            message.channel.send(f'Shut up {message.author.name}.\n')
    

    # SOMEONE REMOVES DIAMONDS
    elif message.content == "!mafia help":
        if opened and (not started):
            await message.channel.send(
                ':arrow_right: Use `!mafia join` to join the session.\n'
                ':arrow_right: Use `!mafia leave` to leave the session.\n'
                ':arrow_right: Use `!mafia godfather` if you want to be the godfather.\n'
                ':arrow_right: Use `!mafia start` to start the game when all players have joined the session.\n\n'
                ':gem: To start the game you need 5 to 12 players in the session.'
            )

    elif message.content[:11] == '!mafia kill':

client.run(TOKEN)
