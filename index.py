import os
from pickle import TRUE

import discord
from discord.ext import commands
from dotenv import load_dotenv
import random

from flask import g

from ExplodingKittens import ExplodingKittens

load_dotenv()
TOKEN = os.getenv('TOKEN')

client = discord.Client()

# global vars
main_channel_name = {}
default_channel_name = 'boardgame'
deck = {}
players = {}
player_channels = {}
state = {}
join_id = {}
host_id = {}
games = ['Exploding Kittens']
min_players = {
    'Exploding Kittens': 2
}
max_players = {
    'Exploding Kittens': 5
}
start_when_ready = {}
init_deck = {
    'Exploding Kittens': [
        'attack',
        'attack',
        'attack',
        'attack',
        'skip',
        'skip',
        'skip',
        'skip',
        'favor',
        'favor',
        'favor',
        'favor',
        'shuffle',
        'shuffle',
        'shuffle',
        'shuffle',
        'see the future',
        'see the future',
        'see the future',
        'see the future',
        'see the future',
        'nope',
        'nope',
        'nope',
        'nope',
        'nope',
        'card1',
        'card1',
        'card1',
        'card1',
        'card2',
        'card2',
        'card2',
        'card2',
        'card3',
        'card3',
        'card3',
        'card3',
        'card4',
        'card4',
        'card4',
        'card4',
        'card5',
        'card5',
        'card5',
        'card5'
    ]
}
plays = {}
main_channel = {}
player_turn = {}
favor_target_list = {}
now_playing = {}
favor_user = {}
hands = {}
double_turn = {}
next_turn = {}
favor = {}
defuse = {}
nope_able = {}
nope_messages = {}
temp_list = {}
favor_target = {}
turn_message = {}
future_message = {}
game_state = {
    'Exploding Kittens': [
        'playing',
        'favor',
        'bomb'
    ]
}
# ----------------------------------------------------------------


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    guilds = client.guilds
    for guild in guilds:
        text_channels = guild.text_channels
        for channel in text_channels:
            if channel.name == 'boardgame':
                main_channel[guild.id] = channel
        for guild in client.guilds:
            var_init(guild)


def var_init(guild):
    global main_channel_name
    global deck
    global players
    global player_channels
    global join_id
    global host_id
    global state
    global start_when_ready
    global plays
    global now_playing
    global player_turn
    global hands
    global next_turn
    global temp_list
    global turn_message
    global defuse
    global nope_able
    global nope_messages
    global favor
    global favor_user
    global favor_target
    global favor_target_list
    global double_turn
    global future_message

    main_channel_name[guild.id] = default_channel_name
    deck[guild.id] = []
    players[guild.id] = []
    player_channels[guild.id] = {}
    join_id[guild.id] = None
    host_id[guild.id] = None
    state[guild.id] = ['ready', '']
    start_when_ready[guild.id] = False
    plays[guild.id] = {}
    now_playing[guild.id] = None
    player_turn[guild.id] = []
    hands[guild.id] = {}
    next_turn[guild.id] = False
    temp_list[guild.id] = []
    turn_message[guild.id] = None

    # Expolding Kittens
    defuse[guild.id] = {}
    nope_able[guild.id] = 0
    nope_messages[guild.id] = {}
    favor[guild.id] = False
    favor_user[guild.id] = None
    favor_target[guild.id] = None
    favor_target_list[guild.id] = []
    double_turn[guild.id] = 0
    future_message[guild.id] = None

    # ----------------------------------------------------------------


@client.event
async def on_message(message):
    global players
    global player_channels
    global plays, hands
    global client
    global favor
    global favor_user
    global favor_target
    global favor_target_list
    global state
    global main_channel
    global turn_message
    global deck
    global defuse
    global double_turn
    global next_turn
    global player_turn
    global future_message
    global nope_able
    global nope_messages
    username = str(message.author).split('#')[0]
    user_message = str(message.content)
    channel = message.channel
    guild = message.guild
    if str(message.author) != str(client.user):
        print(str(channel.name), username, user_message)
        if str(channel.name) == 'boardgame':
            if state[guild.id][0] == 'ready':
                if user_message == '!play' or user_message == '!p':
                    message_to_send = '```Select a game'
                    state[guild.id][0] = 'waiting'
                    for i in range(len(games)):
                        message_to_send += '\n' + str(i+1) + ' : ' + games[i]
                    message_to_send += '\nc : Cancel```'
                    await channel.send(message_to_send)
                    host_id[guild.id] = message.author.id
                    print(user_message, username)
            elif state[guild.id][0] == 'waiting' and message.author.id == host_id[guild.id]:
                print(user_message, username)
                if user_message == 'c':
                    state[guild.id][0] = 'ready'
                    await channel.send('Cancel')
                    await channel.purge()
                elif int(user_message) >= 1 and int(user_message) <= 1:
                    bot_message = await channel.send('Playing ' + games[int(user_message) - 1] + '!' + '\nClick ☑️ to join!')
                    await bot_message.add_reaction('☑️')
                    await bot_message.add_reaction('▶️')
                    state[guild.id][1] = games[int(user_message) - 1]
                    join_id[guild.id] = bot_message.id
                    now_playing[guild.id] = games[int(user_message) - 1]
            elif user_message == 'terminate' or user_message == 'end':
                await clear_text_channel(client.get_guild(guild.id))
            elif state[guild.id][0] == game_state[state[guild.id][1]][2]: # bomb
                index = int(user_message)
                if index >= len(deck[guild.id]):
                    index = -1
                if index != -1:
                    deck[guild.id] = deck[guild.id][:index] + ['bomb'] + deck[guild.id][index:]
                else:
                    deck[guild.id] = deck[guild.id] + ['bomb']
                state[guild.id][0] = 'playing'
            elif state[guild.id][0] == game_state[state[guild.id][1]][1] and message.author == favor_user[guild.id] and int(user_message) - 1 < len(favor_target_list[guild.id]):
                favor_target[guild.id] = favor_target_list[guild.id][int(
                    user_message) - 1]
                [players,
                 player_channels,
                 plays, hands,
                 favor,
                 favor_user,
                 favor_target,
                 favor_target_list,
                 state,
                 main_channel,
                 turn_message,
                 deck,
                 defuse,
                 double_turn,
                 next_turn,
                 player_turn,
                 future_message,
                 nope_able,
                 nope_messages] = await ExplodingKittens(players,
                                                         player_channels,
                                                         plays, hands,
                                                         favor,
                                                         favor_user,
                                                         favor_target,
                                                         favor_target_list,
                                                         state,
                                                         main_channel,
                                                         turn_message,
                                                         deck,
                                                         defuse,
                                                         double_turn,
                                                         next_turn,
                                                         player_turn,
                                                         future_message,
                                                         nope_able,
                                                         nope_messages,
                                                         client,
                                                         guild_id=guild.id,
                                                         GAME_ACTION=True, user=message.author)


@client.event
async def on_raw_reaction_add(payload):
    global players
    global player_channels
    global plays, hands
    global client
    global favor
    global favor_user
    global favor_target
    global favor_target_list
    global state
    global main_channel
    global turn_message
    global deck
    global defuse
    global double_turn
    global next_turn
    global player_turn
    global future_message
    global nope_able
    global nope_messages
    channel_id = payload.channel_id
    guild_id = payload.guild_id
    user_id = payload.user_id
    channel = client.get_channel(channel_id)
    message_id = payload.message_id
    message = await channel.fetch_message(message_id)
    for reaction in message.reactions:
        if str(reaction) == str(payload.emoji):
            print(str(reaction), str(payload.emoji))
            users = await reaction.users().flatten()
            if client.user not in users:
                print('not available')
                return
            else:
                break
    print(payload.member, payload.emoji)
    if str(payload.member) == str(client.user):
        return
    player_channels_list = []
    for player in player_channels[guild_id]:
        player_channels_list.append(player_channels[guild_id][player])
    if str(channel) == 'boardgame':
        if str(payload.emoji) == '☑️':
            if state[guild_id][0] != 'playing' and state[guild_id][0] != 'init':
                if message_id == join_id[guild_id] and payload.member not in players[guild_id]:
                    players[guild_id].append(payload.member)
                if len(players[guild_id]) >= min_players[state[guild_id][1]]:
                    if start_when_ready[guild_id]:
                        state[guild_id][0] = 'init'
                        print(state)
        elif str(payload.emoji) == '▶️':
            if user_id == host_id[guild_id]:
                if len(players[guild_id]) >= min_players[state[guild_id][1]] and len(players[guild_id]) <= max_players[state[guild_id][1]]:
                    state[guild_id][0] = 'init'
                    print(state)
                else:
                    print('not enough players to play')
                    start_when_ready[guild_id] = True
        elif nope_able[guild_id] != 0 and str(payload.emoji) == '🚫':
            pass
        if state[guild_id][0] == 'init':
            state[guild_id][0] = game_state[state[guild_id][1]][0]
            if state[guild_id][1] == games[0]:
                init(state[guild_id][1], guild_id)
                await channel.purge()
                print(deck[guild_id])
                guild = client.get_guild(guild_id)
                for player in players[guild_id]:
                    channel = await create_player_text_channel(guild, player)
                    player_channels[guild_id][player] = channel
                    plays[guild_id][player] = []
                    hands[guild_id][player] = []
                    defuse[guild_id][player] = []
                    nope_messages[guild_id][player] = []
                for player in player_channels[guild_id]:
                    message = await player_channels[guild_id][player].send('defuse')
                    hands[guild_id][player].append(message)
                    defuse[guild_id][player].append(message)
                for i in range(4):
                    for player in player_channels[guild_id]:
                        message = await player_channels[guild_id][player].send(deck[guild_id][0])
                        if 'card' not in deck[guild_id][0] and deck[guild_id][0] != 'nope':
                            await message.add_reaction('☑️')
                        elif deck[guild_id][0] == 'nope':
                            nope_able[guild.id] += 1
                            nope_messages[guild_id][player].append(message)
                        hands[guild_id][player].append(message)
                        deck[guild_id] = deck[guild_id][1:]
                for i in range(len(players[guild_id]) - 1):
                    deck[guild_id].append('bomb')
                deck[guild_id].append('defuse')
                deck[guild_id].append('defuse')
                random.shuffle(deck[guild_id])
                player_turn[guild_id] = players[guild_id].copy()
                random.shuffle(player_turn[guild_id])
                message = await player_channels[guild_id][player_turn[guild_id][0]].send('draw')
                await message.add_reaction('☑️')
                turn_message[guild_id] = message
                await main_channel[guild_id].send(player_turn[guild_id][0].mention + ' turn!')
    elif channel in player_channels_list:
        if state[guild_id][1] == games[0]:
            if state[guild_id][0] != game_state[state[guild_id][1]][2]:
                [players,
                 player_channels,
                 plays, hands,
                 favor,
                 favor_user,
                 favor_target,
                 favor_target_list,
                 state,
                 main_channel,
                 turn_message,
                 deck,
                 defuse,
                 double_turn,
                 next_turn,
                 player_turn,
                 future_message,
                 nope_able,
                 nope_messages] = await ExplodingKittens(players,
                                                         player_channels,
                                                         plays, hands,
                                                         favor,
                                                         favor_user,
                                                         favor_target,
                                                         favor_target_list,
                                                         state,
                                                         main_channel,
                                                         turn_message,
                                                         deck,
                                                         defuse,
                                                         double_turn,
                                                         next_turn,
                                                         player_turn,
                                                         future_message,
                                                         nope_able,
                                                         nope_messages,
                                                         client,
                                                         payload=payload, guild_id=guild_id, channel=channel, message_id=message_id)
                if len(players[guild_id]) == 0:
                    print('end game')
                    await main_channel.send('The winner is ' + player_turn[guild_id].mention + '!!!')
                    await clear_text_channel(client.get_guild(guild_id))
                    var_init(guild)


async def clear_text_channel(guild):
    for player in player_channels[guild.id]:
        await player_channels[guild.id][player].delete()
    state[guild.id] = ['ready', '']


async def create_player_text_channel(guild, user):
    print(guild, user)
    overwrites = {}
    for role in guild.roles:
        overwrites[role] = discord.PermissionOverwrite(read_messages=False)
    overwrites[user] = discord.PermissionOverwrite(read_messages=True)
    channel = await guild.create_text_channel(str(user).split('#')[0] + str(user).split('#')[1], overwrites=overwrites)
    return channel


def init(game, guild_id):
    deck[guild_id] = init_deck[game].copy()
    random.shuffle(deck[guild_id])


@client.event
async def on_raw_reaction_remove(payload):
    channel_id = payload.channel_id
    guild_id = payload.guild_id
    user_id = payload.user_id
    channel = client.get_channel(channel_id)
    message_id = payload.message_id
    if user_id == client.user:
        return
    if str(channel) == 'boardgame':
        if str(payload.emoji) == '☑️':
            if message_id == join_id[guild_id] and payload.member in players[guild_id]:
                players[guild_id].remove(payload.member)
        elif str(payload.emoji) == '▶️':
            if user_id == host_id[guild_id]:
                start_when_ready[guild_id] = False
    elif channel in player_channels[guild_id]:
        if str(channel.name) == str(payload.member).split('#')[0].lower() + str(payload.member).split('#')[1]:
            if str(payload.emoji) == '☑️':
                plays[guild_id][payload.member].remove(message_id)
        else:
            await main_channel[guild_id].send('server owner is now cheating')

client.run(TOKEN)
