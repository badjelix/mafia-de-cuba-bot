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

    print(
        f'{client.user} is connected to the following server:\n'
        f'{guild.name}(id: {guild.id})'
    )


opened = False
started = False
numberOfPlayers = 0
players = {}
box = {}
playerOrder = []


def constructBox():
    global box, numberOfPlayers

    boxString = f'Esta é a caixa para o jogo de {numberOfPlayers} pessoas: \n\n'
    boxString += '----------------- \n'
    boxString += f'Leais - {box["loyal"]} \n'
    boxString += f'Bongós - {box["cop"]} \n'

    if 'taxidriver' in box:
        boxString += f'Taxistas - {box["taxidriver"]} \n'

    boxString += f'Diamantes - {box["diamonds"]} \n'
    boxString += '----------------- \n\n'

    if 'jokers' in box:
        boxString += f'O Padrinho tem {box["jokers"]} Jokers. \n\n'
    else:
        boxString += "O Padrinho não tem jokers!"

    return boxString



@client.event
async def on_message(message):
    global opened, started, players, numberOfPlayers, box

    # Opening game session
    if message.content == '!mafia open':
        if (not opened):
            opened = True
            await message.channel.send(
                'Otários! Para entrarem na sala do Mafia de Cuba escrevam "!mafia join".\n'
                'Para sair, escrevam "!mafia leave". Para começar, "!mafia start".\n'
                'Se quiseres ser o padrinho escreve "!mafia godfather".\n'
                'O nº de jogadores tem de ser entre 5 e 12.'
            )
        else:
            await message.channel.send(
                'Estúpido. O jogo já está aberto.'
            )

    # Player joining
    elif message.content == '!mafia join':
        if opened and (not started) and (message.author.name not in players.keys()):
            print(f'{message.author.name} joined the room')
            players[message.author.name] = 'TBD'
            playerList = '\n - '.join(players.keys())
            await message.channel.send(
                f'{message.author.name} juntou-se ao jogo!\nJogadores na sala [{len(players)}]:\n - {playerList}'
            )
        elif message.author.name in players.keys():
            await message.channel.send(
                f'{message.author.name} és um monte de merda. Tá quieto estúpidx!'
            )
        elif started:
            await message.dm_channel.send(
                f'Desculpa {message.author.name}, mas o jogo já começou. Espera até terminar e entras no próximo!'
            )

    # Player leaving
    elif message.content == "!mafia leave":
        if opened and (not started):
            if message.author.name in players.keys():
                players.pop(message.author.name)
                playerList = '\n - '.join(players.keys())
                await message.channel.send(
                    f'{message.author.name} saiu do jogo! Que conas. \nJogadores na sala [{len(players)}]:\n - {playerList}'
                )

    # Game starting
    elif message.content == "!mafia start":
        if opened:
            numberOfPlayers = len(players)
            if numberOfPlayers < 5 or numberOfPlayers > 12:
                await message.channel.send('O nº de jogadores tem de ser entre 5 e 12!')
            else:
                started = True

                if numberOfPlayers == 5:
                    box = {'loyal':1, 'cop':1, 'diamonds':15}
                elif numberOfPlayers == 6:
                    box = {'loyal':1, 'cop':1, 'taxidriver':1, 'diamonds':15}
                elif numberOfPlayers == 7:
                    box = {'loyal':2, 'cop':1, 'taxidriver':1, 'diamonds':15}
                elif numberOfPlayers == 8:
                    box = {'loyal':3, 'cop':1, 'taxidriver':1, 'jokers':1, 'diamonds':15}
                elif numberOfPlayers == 9:
                    box = {'loyal':4, 'cop':1, 'taxidriver':1, 'jokers':1, 'diamonds':15}
                elif numberOfPlayers == 10:
                    box = {'loyal':4, 'cop':2, 'taxidriver':1, 'jokers':1, 'diamonds':15}
                elif numberOfPlayers == 11:
                    box = {'loyal':4, 'cop':2, 'taxidriver':2, 'jokers':2, 'diamonds':15}
                else:
                    box = {'loyal':5, 'cop':2, 'taxidriver':2, 'jokers':2, 'diamonds':15}

                boxString = constructBox()
                #for player in players.keys():
                #    if players['player'] != 'godfather':
                #        playerOrder.append(player)
                #        random.shuffle(players)
                await message.channel.send(boxString)

        elif (not opened):
            await message.channel.send(
                'Primeiro é preciso abrir a sala com "!mafia open".\n'
                'Caso precises de ajuda usa "!mafia help".'
            )
    
    # Godfather selected
    elif message.content == "!mafia godfather":
        if opened and (not started):
            players[message.author.name] = 'godfather'
            await message.channel.send(f'{message.author.name} é o Padrinho!')

client.run(TOKEN)
