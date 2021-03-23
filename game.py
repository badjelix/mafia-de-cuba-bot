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
godfatherRemoveDiamonds = False
bagDecision = False
boxPassing = False
godfatherAccuse = False
numberOfPlayers = 0
players = {}
box = {}
initialBox = {}
bag = ''
playersOrder = []
godfather = ''
streetUrchin = False
currentPlayer = ''
currentPlayerId = -1


emojis = {
    'loyal' : ':person_in_tuxedo:',
    'agent' : ':cop:',
    'taxidriver' : ':pilot:',
    'thief' : ':detective:',
    'street urchin' : ':child:',
    'godfather' : ':ring:',
    'diamonds' : ':gem:',
    'jokers' : ':whisky:',
    'empty' : ':spider_web:',
}



#####################
# Auxiliary Methods #
#####################

# Constructs Box string given a context and a player name
def constructBox(context, name):
    global box, numberOfPlayers, emojis

    boxString = ''

    if context == 'start':
        boxString += '**Box:**\n\n'
    elif context == 'pass':
        boxString += f'Take the box {name}. Don\'t show it to anyone or Tony Hawkings will kill you.\n\n'
    elif context == 'accuse':
        boxString += f'Godfather {name}! Here\'s your box... Looks like someone has stolen your diamonds!\n'
        boxString += 'Get revenge and retrieve them back using `!mafia accuse <traitor name>`\n\n.'

    boxString += '----------------- \n'
    boxString += f'Loyals - {box["loyals"]} {emojis["loyal"]}\n'
    boxString += f'Agents - {box["agents"]} {emojis["cop"]}\n'

    if 'taxidrivers' in box:
        boxString += f'Taxidrivers - {box["taxidrivers"]} {emojis["taxidriver"]}\n'

    boxString += f'Diamonds - {box["diamonds"]} {emojis["diamonds"]} \n'
    boxString += '----------------- \n\n'

    if context == 'start' or context == 'accuse':
        if 'jokers' in box:
            boxString += f'The Godfather has {box["jokers"]} Jokers {emojis["jokers"]} \n\n'
        else:
            boxString += "The Godfather has no Jokers!\n"

    return boxString


# Constructs Box for when a player asks for the game status
def constructsStatusBox():
    global initialBox

    boxString = f'This was the initial state of the box:\n'

    boxString += '----------------- \n'
    boxString += f'Loyals - {initialBox["loyals"]} {emojis["loyal"]}\n'
    boxString += f'Agents - {initialBox["agents"]} {emojis["cop"]}\n'

    if 'taxidrivers' in box:
        boxString += f'Taxidrivers - {initialBox["taxidrivers"]} {emojis["taxidriver"]}\n'

    boxString += f'Diamonds - {initialBox["diamonds"]} {emojis["diamonds"]} \n'
    boxString += '----------------- \n\n'

    if 'jokers' in box:
        boxString += f'The Godfather has {initialBox["jokers"]} Jokers {emojis["jokers"]} \n\n'
    else:
        boxString += "The Godfather has no Jokers!\n"

    return boxString


# Constructs Table string given the current player name
def constructTable(currentPlayer):
    global numberOfPlayers, playersOrder, godfather, emojis

    tableString = '**Table:**\n'

    for i in range(numberOfPlayers-1):
        if playersOrder[i] == currentPlayer:
            tableString += '(' + str(i+1) + ') **' + playersOrder[i] + '** :briefcase:\n'
        else:
            tableString += '(' + str(i+1) + ') ' + playersOrder[i] + '\n'
    
    if godfather == currentPlayer:
        tableString += '\n **Godfather**: ' + godfather + f' {emojis["godfather"]} :briefcase:\n\n'
    else:
        tableString += '\n **Godfather**: ' + godfather + f' {emojis["godfather"]}\n\n'

    return tableString


# Constructs Bag Options string
def constructBagOptions():
    global box

    bagOptionsString = 'You\'re the first player with the box! You get to hide a character in the bag, or not, you choose!\n' + \
                       ':arrow_right: Use `!mafia bag loyal` if you want to hide a Loyal.\n' + \
                       ':arrow_right: Use `!mafia bag agent` if you want to hide an Agent.\n'

    if 'taxidrivers' in box:
        bagOptionsString += ':arrow_right: Use `!mafia bag taxidriver` if you want to hide a Taxidriver.\n'

    bagOptionsString += ':arrow_right: Use `!mafia bag none` if you don\'t want to hide a character.\n'

    return bagOptionsString


# Constructs Options string possibly with the Street Urchin option
def constructOptions(streetUrchin):
    global box
    optionsString = ''

    if 'loyals' in box and box["loyals"] > 0:
        optionsString += ':arrow_right: Use `!mafia take loyal` if you want to be a Loyal.\n'
    if 'agents' in box and box["agents"] > 0:
        optionsString += ':arrow_right: Use `!mafia take agent` if you want to be an Agent.\n'
    if 'taxidrivers' in box and box["taxidrivers"] > 0:
        optionsString += ':arrow_right: Use `!mafia take taxidriver` if you want to be a Taxidriver.\n'
    if 'diamonds' in box and box["diamonds"] > 0:
        optionsString += ':arrow_right: Use `!mafia take <number of diamonds> diamonds` if you want to be a Thief and remove <number of diamonds> diamonds.\n'
    if streetUrchin:
        optionsString += ':arrow_right: Use `!mafia take street urchin` if you want to be a Street Urchin.\n'

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


# Gets member by name
def getMember(name):
    for member in guild.members:
        if member.name == name:
            return member


#####################
# Game Core Methods #
#####################

# Method that handles the different messages the client receives from Discord
@client.event
async def on_message(message):
    global guild, guildChannel, opened, started, players, currentPlayer, currentPlayerId, numberOfPlayers, box, bag, \
           godfather, godfatherRemoveDiamonds, bagDecision, boxPassing, godfatherAccuse


    # OPEN GAME SESSION
    if message.content == '!mafia open':
        if not opened:
            opened = True
            await guildChannel.send(
                ':dagger: Buenas noches hijos de puta! :dagger:\n\n'
                ':arrow_right: Use `!mafia join` to join the session.\n'
                ':arrow_right: Use `!mafia leave` to leave the session.\n'
                ':arrow_right: Use `!mafia godfather` if you want to be the godfather.\n'
                ':arrow_right: Use `!mafia start` to start the game when all players have joined the session.\n'
                ':arrow_right: Use `!mafia help` if you are lost.\n\n'
                ':gem: To start the game you need 5 to 12 players in the session.'
            )
        else:
            await guildChannel.send(f'{message.author.name} is a Tony Hawking. The game room is already opened...')


    # PLAYER JOINS
    elif message.content == '!mafia join':
        if opened and (not started) and (message.author.name not in players.keys()):
            players[message.author.name] = ['TBD', 'alive']
            playerList = '\n - '.join(players.keys())
            if godfather != '':
                playerList += f'\n\n The **Godfather** is {godfather} {emojis["godfather"]}'
            await guildChannel.send(f'{message.author.name} joined the game! :gun:\n' +
                                    f'Players in the room **[{len(players)}]**:\n - {playerList}'
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
                                        f'Players in the room **[{len(players)}]**:\n - {playerList}'
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
                    initialBox = box
                elif numberOfPlayers == 6:
                    box = {'loyals':1, 'agents':1, 'taxidrivers':1, 'diamonds':15}
                    initialBox = box
                elif numberOfPlayers == 7:
                    box = {'loyals':2, 'agents':1, 'taxidrivers':1, 'diamonds':15}
                    initialBox = box
                elif numberOfPlayers == 8:
                    box = {'loyals':3, 'agents':1, 'taxidrivers':1, 'jokers':1, 'diamonds':15}
                    initialBox = box
                elif numberOfPlayers == 9:
                    box = {'loyals':4, 'agents':1, 'taxidrivers':1, 'jokers':1, 'diamonds':15}
                    initialBox = box
                elif numberOfPlayers == 10:
                    box = {'loyals':4, 'agents':2, 'taxidrivers':1, 'jokers':1, 'diamonds':15}
                    initialBox = box
                elif numberOfPlayers == 11:
                    box = {'loyals':4, 'agents':2, 'taxidrivers':2, 'jokers':2, 'diamonds':15}
                    initialBox = box
                else:
                    box = {'loyals':5, 'agents':2, 'taxidrivers':2, 'jokers':2, 'diamonds':15}
                    initialBox = box

                for player in players.keys():
                    if player != godfather:
                        playersOrder.append(player)

                random.shuffle(playersOrder)

                tableString = constructTable(godfather)

                boxString = constructBox('start', message.author.name)

                await guildChannel.send(tableString + boxString)

                godfatherMember = getMember(godfather)

                godfatherRemoveDiamonds = True

                await godfatherMember.create_dm()
                await godfatherMember.dm_channel.send(f'Godfather {godfather}, ' +
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
            players[message.author.name] = ['godfather', 'alive']
            godfather = message.author.name
            await guildChannel.send(f'{message.author.name} is the Godfather! :ring:')


    # GODFATHER REMOVES DIAMONDS FROM THE BOX
    elif message.content[:13] == '!mafia remove':

        messageSplit = message.content.split()
        matches = bool(re.match('^[-+]?\d+$', messageSplit[2]))

        if matches and godfatherRemoveDiamonds and (message.author.name == godfather) and (int(messageSplit[2]) <= 5 and int(messageSplit[2]) >= 0):
            box["diamonds"] = box["diamonds"] - int(messageSplit[2])

            godfatherRemoveDiamonds = False
            bagDecision = True
            currentPlayer = playersOrder[0]
            currentPlayerId = 0

            await guildChannel.send('**The Godfather passed the box!**\n\n' + constructTable(currentPlayer))

            playerMember = getMember(currentPlayer)

            await playerMember.create_dm()
            await playerMember.dm_channel.send(constructBox('pass', currentPlayer) + constructBagOptions())

        elif matches and godfatherRemoveDiamonds and (message.author.name == godfather) and (int(messageSplit[2]) > 5 or int(messageSplit[2]) < 0):
            await message.channel.send('You can only remove from 0 to 5 diamonds.')
        
        elif not matches:
            await message.channel.send('You piece of shit.')


    # FIRST PLAYER HIDES A PIECE IN THE BAG
    elif message.content[:10] == '!mafia bag':

        if bagDecision and (message.author.name == currentPlayer):

            messageSplit = message.content.split()

            # Player bags loyal
            if messageSplit[2] == 'loyal':
                if box["loyals"] > 0:
                    box["loyals"] = box["loyals"] - 1
                    bag = 'loyal'
                    bagDecision = False
                    boxPassing = True
                    playerMember = getMember(currentPlayer)
                    await playerMember.create_dm()
                    await playerMember.dm_channel.send(constructBox('pass', currentPlayer) + constructOptions(False))

                else:
                    await message.channel.send('Duh.\n')

            # Player bags agent
            elif messageSplit[2] == 'agent':
                if box["agents"] > 0:
                    box["agents"] = box["agents"] - 1
                    bag = 'agent'
                    bagDecision = False
                    boxPassing = True
                    playerMember = getMember(currentPlayer)
                    await playerMember.create_dm()
                    await playerMember.dm_channel.send(constructBox('pass', currentPlayer) + constructOptions(False))

                else:
                    await message.channel.send('Duh.\n')

            # Player bags taxidriver
            elif messageSplit[2] == 'taxidriver':
                if box["taxidrivers"] > 0:
                    box["taxidrivers"] = box["taxidrivers"] - 1
                    bag = 'taxidriver'
                    bagDecision = False
                    boxPassing = True
                    playerMember = getMember(currentPlayer)
                    await playerMember.create_dm()
                    await playerMember.dm_channel.send(constructBox('pass', currentPlayer) + constructOptions(False))

                else:
                    message.channel.send('Duh.\n')

            # Player bags nothing
            elif messageSplit[2] == 'none':
                bag = 'empty'
                bagDecision = False
                boxPassing = True
                playerMember = getMember(currentPlayer)
                await playerMember.create_dm()
                await playerMember.dm_channel.send(constructOptions(False))


    # SOMEONE TAKES SOMETHING OUT OF THE BOX
    elif message.content[:11] == '!mafia take':

        if boxPassing and (message.author.name == currentPlayer):

            messageSplit = message.content.split()
            matchesWord = bool(re.match('^[a-z]+$', messageSplit[2]))
            matchesNumber = bool(re.match('^[0-9]+$', messageSplit[2]))

            if matchesWord:
                # Player takes loyal
                if messageSplit[2] == 'loyal':
                    if box["loyals"] > 0:
                        box["loyals"] = box["loyals"] - 1
                        players[message.author.name] = ['loyal','alive']
                        if currentPlayerId == numberOfPlayers - 2:
                            boxPassing = False
                            godfatherAccuse = True
                            await guildChannel.send('**The box has returned to the Godfather!**\n\n' + constructTable(godfather) +
                                                    f'\n:gem: **Godfather {godfather}!** Someone has stolen your precious diamonds! :face_with_symbols_over_mouth:\n' +
                                                    ':dagger: Hijos de puta, traidores! :dagger:\n' +
                                                    '**The Godfather must find the thieves!**')
                            godfatherMember = getMember(godfather)
                            await godfatherMember.create_dm()
                            await godfatherMember.dm_channel.send(constructBox('accuse', godfather))
                        else:
                            message = f'**{currentPlayer} passed the box!**\n\n'
                            currentPlayerId += 1
                            currentPlayer = playersOrder[currentPlayerId]
                            message += constructTable(currentPlayer)
                            await guildChannel.send(message)
                            playerMember = getMember(currentPlayer)
                            await playerMember.create_dm()
                            await playerMember.dm_channel.send(constructBox('pass', currentPlayer) + constructOptions(checkStreetUrchin()))
                    else:
                        await message.channel.send('Duh.\n')
                
                # Player takes agent
                elif messageSplit[2] == 'agent':
                    if box["agents"] > 0:
                        box["agents"] = box["agents"] - 1
                        players[message.author.name] = ['agent','alive']
                        if currentPlayerId == numberOfPlayers - 2:
                            boxPassing = False
                            godfatherAccuse = True
                            await guildChannel.send('**The box has returned to the Godfather!**\n\n' + constructTable(godfather) +
                                                    f'\n:gem: **Godfather {godfather}!** Someone has stolen your precious diamonds! :face_with_symbols_over_mouth:\n' +
                                                    ':dagger: Hijos de puta, traidores! :dagger:\n' +
                                                    '**The Godfather must find the thieves!**')
                            godfatherMember = getMember(godfather)
                            await godfatherMember.create_dm()
                            await godfatherMember.dm_channel.send(constructBox('accuse', godfather))
                        else:
                            message = f'**{currentPlayer} passed the box!**\n\n'
                            currentPlayerId += 1
                            currentPlayer = playersOrder[currentPlayerId]
                            message += constructTable(currentPlayer)
                            await guildChannel.send(message)
                            playerMember = getMember(currentPlayer)
                            await playerMember.create_dm()
                            await playerMember.dm_channel.send(constructBox('pass', currentPlayer) + constructOptions(checkStreetUrchin()))
                    else:
                        await message.channel.send('Duh.\n')

                # Player takes taxidriver
                elif messageSplit[2] == 'taxidriver':
                    if box["taxidrivers"] > 0:
                        box["taxidrivers"] = box["taxidrivers"] - 1
                        players[message.author.name] = ['taxidriver','alive']
                        if currentPlayerId == numberOfPlayers - 2:
                            boxPassing = False
                            godfatherAccuse = True
                            await guildChannel.send('**The box has returned to the Godfather!**\n\n' + constructTable(godfather) +
                                                    f'\n:gem: **Godfather {godfather}!** Someone has stolen your precious diamonds! :face_with_symbols_over_mouth:\n' +
                                                    ':dagger: Hijos de puta, traidores! :dagger:\n' +
                                                    '**The Godfather must find the thieves!**')
                            godfatherMember = getMember(godfather)
                            await godfatherMember.create_dm()
                            await godfatherMember.dm_channel.send(constructBox('accuse', godfather))
                        else:
                            message = f'**{currentPlayer} passed the box!**\n\n'
                            currentPlayerId += 1
                            currentPlayer = playersOrder[currentPlayerId]
                            message += constructTable(currentPlayer)
                            await guildChannel.send(message)
                            playerMember = getMember(currentPlayer)
                            await playerMember.create_dm()
                            await playerMember.dm_channel.send(constructBox('pass', currentPlayer) + constructOptions(checkStreetUrchin()))
                    else:
                        await message.channel.send('Duh.\n')

                # Player takes street urchin
                elif messageSplit[2] == 'street' and messageSplit[3] == 'urchin':
                    if checkStreetUrchin():
                        players[message.author.name] = ['street urchin','alive']
                        if currentPlayerId == numberOfPlayers - 2:
                            boxPassing = False
                            godfatherAccuse = True
                            await guildChannel.send('**The box has returned to the Godfather!**\n\n' + constructTable(godfather) +
                                                    f'\n:gem: **Godfather {godfather}!** Someone has stolen your precious diamonds! :face_with_symbols_over_mouth:\n' +
                                                    ':dagger: Hijos de puta, traidores! :dagger:\n' +
                                                    '**The Godfather must find the thieves!**')
                            godfatherMember = getMember(godfather)
                            await godfatherMember.create_dm()
                            await godfatherMember.dm_channel.send(constructBox('accuse', godfather))
                        else:
                            message = f'**{currentPlayer} passed the box!**\n\n'
                            currentPlayerId += 1
                            currentPlayer = playersOrder[currentPlayerId]
                            message += constructTable(currentPlayer)
                            await guildChannel.send(message)
                            playerMember = getMember(currentPlayer)
                            await playerMember.create_dm()
                            await playerMember.dm_channel.send(constructBox('pass', currentPlayer) + constructOptions(checkStreetUrchin()))
            
            # Player takes diamonds
            elif matchesNumber:
                if len(messageSplit) == 4:
                    if int(messageSplit[2]) >= 0:
                        if messageSplit[3] == 'diamonds':
                            if box["diamonds"] >= int(messageSplit[2]):
                                box["diamonds"] = box["diamonds"] - int(messageSplit[2])
                                players[message.author.name] = ['thief ' + messageSplit[2],'alive']
                                if currentPlayerId == numberOfPlayers - 2:
                                    boxPassing = False
                                    godfatherAccuse = True
                                    await guildChannel.send('**The box has returned to the Godfather!**\n\n' + constructTable(godfather) +
                                                            f'\n:gem: **Godfather {godfather}!** Someone has stolen your precious diamonds! :face_with_symbols_over_mouth:\n' +
                                                            ':dagger: Hijos de puta, traidores! :dagger:\n' +
                                                            '**The Godfather must find the thieves!**')
                                    godfatherMember = getMember(godfather)
                                    await godfatherMember.create_dm()
                                    await godfatherMember.dm_channel.send(constructBox('accuse', godfather))
                                else:
                                    message = f'**{currentPlayer} passed the box!**\n\n'
                                    currentPlayerId += 1
                                    currentPlayer = playersOrder[currentPlayerId]
                                    message += constructTable(currentPlayer)
                                    await guildChannel.send(message)
                                    playerMember = getMember(currentPlayer)
                                    await playerMember.create_dm()
                                    await playerMember.dm_channel.send(constructBox('pass', currentPlayer) + constructOptions(checkStreetUrchin()))
                            else:
                                await message.channel.send('You are taking too much diamonds')
                        else:
                            await message.channel.send(f'Your message is stupid.')
                    else:
                        await message.channel.send(f'Stop being retardation, {message.author.name}.')
                else:
                    await message.channel.send(f'Your message is stupid.')
        
        else:
            await message.channel.send(f'Shut up {message.author.name}.\n')


    # GODFATHER ACCUSES THIEF
    elif message.content[:13] == '!mafia accuse':
        if godfatherAccuse and message.author.name == godfather:

            traitor = message.content[14:]

            if traitor in players.keys():
                # reveal character
                endAccusing = False
                updateJoker = True

                players[traitor][1] = 'dead'

                if players[traitor][0] == 'loyal':
                    await guildChannel.send(f'**Oh no! {traitor} is a Loyal!** {emojis["loyal"]} :gun:\n')
                elif players[traitor][0] == 'agent':
                    endAccusing = True
                    updateJoker = False
                    await guildChannel.send(f'**OHHHHH! :astonished: {traitor} is an Agent!!!** {emojis["agent"]} :gun:\n')
                elif players[traitor][0] == 'taxidriver':
                    await guildChannel.send(f'**{traitor} is a Taxidriver.** {emojis["taxidriver"]} :gun:\n')
                elif players[traitor][0][:5] == 'thief':
                    endAccusing = True
                    updateJoker = False
                    for player in list(players.values()):
                        if player[0][:5] == 'thief' and player[1] == 'alive':
                            endAccusing = False
                            break
                    diamonds = players[traitor][0].split()[1]
                    await guildChannel.send(f'**Good job! {traitor} is a Thief that stole {diamonds} diamonds!** {emojis["thief"]} :gun:\n')
                elif players[traitor][0] == 'street urchin':
                    await guildChannel.send(f'**Oh no! {traitor} is a Street Urchin!** {emojis["street urchin"]} :gun:\n')

                if updateJoker and ('jokers' in box) and box["jokers"] > 0:
                    box["jokers"] = box["jokers"] - 1
                    await guildChannel.send(f'Jokers left for the Godfather: {box["jokers"]} {emojis["jokers"]}')
                elif updateJoker and ('jokers' not in box) or box["jokers"] == 0:
                    endAcussing = True
                    await guildChannel.send('The Godfather has no Jokers left! He/She was not able to find the traitors!\n')

                if endAccusing:
                    # show winners
                    winners = []
                    winnersIds = []
                    taxidriversId = []
                    godfatherWins = False

                    if players[traitor][0] == 'loyal' or players[traitor][0] == 'taxidriver' or 'street urchin':
                        for player in list(players.items()):
                            if player[1][0][:5] == 'thief' or player[1][0] == 'street urchin':
                                winners.append(player[0])
                    elif players[traitor][0] == 'agent':
                        for player in list(players.items()):
                            if player[1][0] == 'agent' and player[1][1] == 'dead':
                                winners.append(player[0])
                                break
                    elif players[traitor][0][:5] == 'thief':
                        godfatherWins = True
                        for player in list(players.items()):
                            if player[1][0] == 'loyal':
                                winners.append(player[0])
                    

                    for winner in winners:
                        for i in range(numberOfPlayers-1):
                            if playersOrder[i] == winner:
                                winnersIds.append(i)

                    for player in list(players.items()):
                        if player[1][0] == 'taxidriver':
                            for i in range(numberOfPlayers-1):
                                if playersOrder[i] == player[0]:
                                    taxidriversId.append(i)

                    for taxidriver in taxidriversId:
                        for winner in winnersIds:
                            if taxidriver == (winner + 1) % (numberOfPlayers-1):
                                winners.append(playersOrder[taxidriver])

                    
                    finalResults = '**FINAL RESULTS**\n\n'

                    for i in range(numberOfPlayers-1):
                        if playersOrder[i] in winners:
                            finalResults += '(' + str(i+1) + ') **' + playersOrder[i] + '** :military_medal: '
                        else:
                            finalResults += '(' + str(i+1) + ')' + playersOrder[i] + ':skull: '

                        finalResults += emojis[players[playersOrder[i]][0]] + ' '

                        if i == 0:
                            finalResults += '[' + emojis[bag] + ']\n'
                    
                    if godfatherWins:
                        finalResults += '\n **Godfather**: **' + godfather + '** :military_medal: :ring:\n\n'
                    else:
                        finalResults += '\n **Godfather**: ' + godfather + ' :skull: :ring:\n\n'

                    await guildChannel.send(finalResults)

            else:
                await message.channel.send(f'{traitor} is not in the room. Check if you spelled his/her name right.')
            
        else:
            await message.channel.send(f'Stop it, {message.author.name}')
    

    # SOMEONE ASKS FOR HELP
    elif message.content == "!mafia help":
        if opened and (not started):
            await message.channel.send(
                ':arrow_right: Use `!mafia join` to join the session.\n'
                ':arrow_right: Use `!mafia leave` to leave the session.\n'
                ':arrow_right: Use `!mafia godfather` if you want to be the godfather.\n'
                ':arrow_right: Use `!mafia start` to start the game when all players have joined the session.\n'
                ':arrow_right: Use `!mafia help` if you are lost.\n\n'
                ':gem: To start the game you need 5 to 12 players in the session.'
            )

    # MAFIA STATUS
    elif message.content == "!mafia status":
        if opened and not started:
            playerList = '\n - '.join(players.keys())
            if godfather != '':
                playerList += f'\n\n The **Godfather** is {godfather} {emojis["godfather"]}'
            await guildChannel.send(f'Players in the room **[{len(players)}]**:\n - {playerList}')
        elif started:
            playerList = '\n - '.join(players.keys())
            await guildChannel.send(f'Players in the room **[{len(players)}]**:\n - {playerList}\n' + constructsStatusBox())





###################
# Run the Client! #
###################

client.run(TOKEN)
