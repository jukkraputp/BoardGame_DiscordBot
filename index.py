import os
import asyncio

import discord
from dotenv import load_dotenv
from flask import g

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
music_channel = {}
music_queue = {}
music_caller = {}
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
            await temp_channel.send('Please use !setup <text_channel> command first!')
            pass
        var_init(guild)


def var_init(guild):
    global players
    global player_channels
    global join_message
    global host
    global state
    global start_when_ready
    global music_channel
    global music_queue
    global music_caller

    players[guild] = []
    player_channels[guild] = {}
    join_message[guild] = None
    host[guild] = None
    state[guild] = ['ready', None]
    start_when_ready[guild] = False
    emotable[guild] = []
    music_channel[guild] = None
    music_queue[guild] = []
    music_caller[guild] = None

    # ----------------------------------------------------------------


@client.event
async def on_message(message):
    username = str(message.author).split('#')[0]
    user_message = str(message.content)
    channel = message.channel
    guild = message.guild

    if user_message == 'terminate' or user_message == 'end':
        await clear_text_channel(guild)
        await main_channel[guild].purge()
    elif music_caller is None and user_message[:5] == '!music' and user_message[5] == ' ':
        voice_channel = message.author.voice.channel
        if voice_channel is not None:
            music_channel[guild] = voice_channel
        try:
            message = await client.wait_for('message', timeout=60, check=is_call_music)
        except asyncio.TimeoutError:
            return 'c'
        else:
            return int(message.content)
        music_name = user_message[6:]
        music_queue[guild].append(music_name)
        voice_client = await music_channel.connect()
        await PLAY_MUSIC(guild, voice_client)    
    if state[guild][0] == 'playing':
        return
    if str(message.author) != str(client.user):
        print('from index.py', guild.name, channel.name, username, user_message)
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
                elif int(user_message) >= 1 and int(user_message) <= len(games):
                    bot_message = await channel.send('Playing ' + games[int(user_message) - 1] + '!' + '\nClick ☑️ to join!')
                    await bot_message.add_reaction('☑️')
                    await bot_message.add_reaction('▶️')
                    emotable[guild].append(bot_message)
                    state[guild][1] = games[int(user_message) - 1]
                    join_message[guild] = bot_message

                    state[guild][0] = str(
                        state[guild][1]) + ' waiting for players'


def is_call_music(m):
    return m.author == music_caller[m.guild]


async def PLAY_MUSIC(guild, voice_client):
    pass


game_start = False


@client.event
async def on_raw_reaction_add(payload):
    if payload.member == client.user:
        return
    global game_start
    global state
    guild = client.get_guild(payload.guild_id)
    print('add')
    if state[guild][0] == str(state[guild][1]) + ' waiting for players':
        print('state pass')
        message = join_message[guild]
        print(str(message.channel))
        if message.channel == main_channel[guild]:
            print('channel pass')
            reaction = payload.emoji
            user = payload.member
            print(str(user), str(reaction))
            if str(reaction) == '☑️':
                players[guild].append(user)
                for player in players[guild]:
                    print(str(player))
            elif str(reaction) == '▶️' and user == host[guild]:
                game_start = True
            print(game_start, len(
                players[guild]), min_players[state[guild][1]], max_players[state[guild][1]])
            if state[guild][1] == games[0]:
                if game_start and len(players[guild]) >= min_players[state[guild][1]] and len(players[guild]) <= max_players[state[guild][1]]:
                    print('game start')
                    for player in players[guild]:
                        channel = await create_player_text_channel(guild, player)
                        player_channels[guild][player] = channel
                    await main_channel[guild].purge()
                    state[guild][0] = 'playing'
                    # game start ----------------------------------------------------------------
                    winner = await asyncio.create_task(EXPLODINGKITTENS(guild))
                    print('The winner is', winner, '!!!')
                    # game end ------------------------------------------------------------------
                    var_init(guild)
                    return


@client.event
async def on_raw_reaction_remove(payload):
    if payload.member == client.user:
        return
    global game_start
    global state
    guild = client.get_guild(payload.guild_id)
    print('remove')
    if state[guild][0] == str(state[guild][1]) + ' waiting for players':
        print('state pass')
        message = join_message[guild]
        print(str(message.channel))
        if message.channel == main_channel[guild]:
            print('channel pass')
            reaction = payload.emoji
            user = await guild.fetch_member(payload.user_id)
            print(str(user), str(reaction))
            if str(reaction) == '☑️':
                players[guild].remove(user)
                for player in players[guild]:
                    print(str(player))
            elif str(reaction) == '▶️' and user == host[guild]:
                game_start = False
            print(game_start, len(
                players[guild]), min_players[state[guild][1]], max_players[state[guild][1]])


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
