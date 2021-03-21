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
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )

    members = '\n - '.join([member.name for member in guild.members])
    print(f'Guild Members:\n - {members}')


players = []
on = 0
begin = 0
nop = 0
box = [0, 1, 2, 3, 4]
# 0 - Leais
# 1 - Bongó
# 2 - Taxi
# 3 - Jokers
# 4 - Diamantes


@client.event
async def on_message(open_m):
    global on
    if on == 0:
        if open_m.content == 'open_mafia':
            global on
            on = 1
            await open_m.channel.send(
                "Pequeñitos! Para jogar Mafia de Cuba escrevam 'join_mafia'. \n"
                "Para sair, escrevam 'leave_mafia'. Para começar, 'start_mafia'. \n"
                "O nº de jogadores tem de ser entre 6 e 12."
            )


@client.event
async def on_message(join):
    global on
    if on:
        global begin
        if begin == 0:
            if join.content == 'join_mafia':
                global players
                players.append(join.author)
                await join.channel.send(
                    '{} juntou-se ao jogo. \n'
                    'Nº de jogadores {}'.format(join.author, len(players))
                )

            elif join.content == 'leave_mafia':
                global players
                if join.author in players:
                    players.remove(join.author)
                    await join.channel.send(
                        '{} saiu do jogo. \n'
                        'Nº de jogadores {}'.format(join.author, len(players))
                    )
            elif join.content == 'start_mafia':
                global players
                global nop
                nop = len(players)
                if nop < 6 or nop > 12:
                    await join.channel.send('O nº de jogadores tem de ser entre 6 e 12!')
                else:
                    global begin
                    begin = 1

                    global box
                    if nop == 6:
                        box = [1, 1, 1, 0, 15]
                    elif nop == 7:
                        box = [2, 1, 1, 0, 15]
                    elif nop == 8:
                        box = [3, 1, 1, 1, 15]
                    elif nop == 9:
                        box = [4, 1, 1, 1, 15]
                    elif nop == 10:
                        box = [4, 2, 1, 1, 15]
                    elif nop == 11:
                        box = [4, 2, 2, 2, 15]
                    else:
                        box = [5, 2, 2, 2, 15]

                    await join.channel.send(
                        'Esta é a caixa para o jogo de {} pessoas: \n'
                        '\n'
                        '----------------- \n'
                        'Leais - {} \n'
                        'Bongós - {} \n'
                        'Taxistas - {} \n'
                        'Diamantes - {} \n'
                        '----------------- \n'
                        '\n'
                        'O Padrinho tem {} Jokers. \n'
                        '\n'
                        "Para ser Padrinho escreve 'me_god'. \n"
                        "Para Padrinho aleatório 'random_god'.".format(nop, box[0], box[1], box[2], box[4], box[3])
                    )


@client.event
async def on_message(god):
    if begin == 1
    random.shuffle(players)


client.run(TOKEN)
