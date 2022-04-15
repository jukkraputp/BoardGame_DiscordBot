import os
import asyncio
import sys

import discord
from dotenv import load_dotenv

from ExplodingKittens import ExplodingKittens

load_dotenv()
TOKEN = os.getenv('TOKEN')

client = discord.Client()

# global vars
players = {}
player_channels = {}
state = {}
join_message = {}
host = {}
games = ['Exploding Kittens']
min_players = {
    'Exploding Kittens': 2
}
max_players = {
    'Exploding Kittens': 5
}
start_when_ready = {}
main_channel = {}
emotable = {}
# ----------------------------------------------------------------


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    guilds = client.guilds
    for guild in guilds:
        main_channel[guild] = None
        temp_channel = None
        for channel in guild.text_channels:
            if channel.name == 'boardgame':
                main_channel[guild] = channel
                print(f'{guild.name} has default channel!')
                break
            elif channel.name == 'general' or channel == guild.text_channels[0]:
                temp_channel = channel
        if main_channel[guild] is None:
            # await temp_channel.send('Please use !setup <text_channel> command first!')
            pass
        var_init(guild)


def var_init(guild):
    global players
    global player_channels
    global join_message
    global host
    global state
    global start_when_ready

    players[guild] = []
    player_channels[guild] = {}
    join_message[guild] = None
    host[guild] = None
    state[guild] = ['ready', None]
    start_when_ready[guild] = False
    emotable[guild] = []

    # ----------------------------------------------------------------


@client.event
async def on_message(message):
    username = str(message.author).split('#')[0]
    user_message = str(message.content)
    channel = message.channel
    guild = message.guild
    if user_message == 'terminate' or user_message == 'end':
        await clear_text_channel(guild)
        sys.exit()
    
    if str(message.author) != str(client.user):
        print(guild.name, channel.name, username, user_message)
        if '!setup ' in user_message:
            channel_name = user_message[7:]
            if main_channel[guild] != None:
                await main_channel[guild].delete()
            main_channel[guild] = await guild.create_text_channel(channel_name)
        elif channel == main_channel[guild]:
            if state[guild][0] == 'ready':
                if user_message == '!play' or user_message == '!p':
                    message_to_send = '```Select a game'
                    state[guild][0] = 'waiting'
                    for i in range(len(games)):
                        message_to_send += '\n' + str(i+1) + ' : ' + games[i]
                    message_to_send += '\nc : Cancel```'
                    await channel.send(message_to_send)
                    host[guild] = message.author
            elif state[guild][0] == 'waiting' and message.author == host[guild]:
                if user_message == 'c':
                    state[guild][0] = 'ready'
                    await channel.send('Cancel')
                    await channel.purge()
                elif int(user_message) >= 1 and int(user_message) <= 1:
                    bot_message = await channel.send('Playing ' + games[int(user_message) - 1] + '!' + '\nClick ☑️ to join!')
                    await bot_message.add_reaction('☑️')
                    await bot_message.add_reaction('▶️')
                    emotable[guild].append(bot_message)
                    state[guild][1] = games[int(user_message) - 1]
                    join_message[guild] = bot_message

                    task_add = asyncio.create_task(wait_add_player(state[guild][1]))
                    task_remove = asyncio.create_task(wait_remove_player())

                    await task_add
                    await task_remove


game_start = False


async def wait_add_player(game):
    global game_start

    try:
        reaction, user = await client.wait_for('reaction_add', timeout=600, check=check_emotable)
    except asyncio.TimeoutError:
        pass
    else:
        message = reaction.message
        guild = message.guild
        if str(reaction) == '☑️' and reaction.message == join_message[guild]:
            players[guild].append(user)
            for player in players[guild]:
                print(str(player))
        elif str(reaction) == '▶️' and user == host[guild]:
            game_start = True
        print(game_start, len(players[guild]), min_players[state[guild][1]], max_players[state[guild][1]])
        if game == games[0]:
            if game_start and len(players[guild]) >= min_players[state[guild][1]] and len(players[guild]) <= max_players[state[guild][1]]:
                print('game start')
                for player in players[guild]:
                    channel = await create_player_text_channel(guild, player)
                    player_channels[guild][player] = channel
                # game start ----------------------------------------------------------------
                winner = await asyncio.create_task(EXPLODINGKITTENS(guild))
                print('The winner is', winner, '!!!')
                # game end ------------------------------------------------------------------
                var_init(guild)
            else:
                await wait_add_player(game)


async def wait_remove_player():
    global game_start

    try:
        reaction, user = await client.wait_for('reaction_remove', timeout=600, check=check_emotable)
    except asyncio.TimeoutError:
        pass
    else:
        message = reaction.message
        guild = message.guild
        if str(reaction) == '☑️' and reaction.message == join_message[guild]:
            players[guild].remove(user)
            for player in players[guild]:
                print(str(player))
        elif str(reaction) == '▶️' and user == host[guild]:
            game_start = False
        else:
            await wait_remove_player()


def check_emotable(reaction, user):
    message = reaction.message
    guild = message.guild
    if message in emotable[guild]:
        return True
    return True


async def clear_text_channel(guild):
    for player in player_channels[guild]:
        await player_channels[guild][player].delete()
    state[guild] = ['ready', '']


async def create_player_text_channel(guild, user):
    print(f'create text channel in {guild} for {user}')
    overwrites = {}
    for role in guild.roles:
        overwrites[role] = discord.PermissionOverwrite(read_messages=False)
    overwrites[user] = discord.PermissionOverwrite(read_messages=True)
    channel = await guild.create_text_channel(str(user).split('#')[0] + str(user).split('#')[1], overwrites=overwrites)
    return channel


async def EXPLODINGKITTENS(guild):
    await ExplodingKittens(client, guild, player_channels[guild], players[guild], main_channel[guild])
    return


client.run(TOKEN)
