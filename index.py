import os

import discord
from discord.ext import commands
from dotenv import load_dotenv
from flask import g

load_dotenv()
TOKEN = os.getenv('TOKEN')

client = discord.Client()

deck = {}
players = {}
player_channels = {}
state = {}
join_id = {}
host_id = {}
games = ['exploding kittens']
min_players = {
    'exploding kittens': 2
}
start_when_ready = {}
init_deck = {
    'exploding kittens': [
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


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    guild = client.get_guild(886934614655000656)
    # await guild.create_text_channel('cool-channel')
    text_channels = guild.text_channels
    for channel in text_channels:
        if channel.name == 'boardgame':
            main_channel[guild.id] = channel
    ''' voice_channels = guild.voice_channels
    for channel in voice_channels:
        if channel.name == 'test':
            await channel.delete() '''
    roles = guild.roles
    for guild in client.guilds:
        deck[guild.id] = []
        players[guild.id] = []
        player_channels[guild.id] = {}
        join_id[guild.id] = ''
        host_id[guild.id] = ''
        state[guild.id] = ['ready', '']
        start_when_ready[guild.id] = False
        plays[guild.id] = {}


@client.event
async def on_message(message):
    username = str(message.author).split('#')[0]
    user_message = str(message.content)
    channel = message.channel
    guild = message.guild
    if str(message.author) != 'ProjectBeta#6332':
        print(str(channel.name))
        if str(channel.name) == 'boardgame':
            if state[guild.id][0] == 'ready':
                if user_message == '!play' or user_message == '!p':
                    await channel.send('Select 1 game')
                    state[guild.id][0] = 'waiting'
                    for i in range(len(games)):
                        await channel.send(str(i+1) + ' : ' + games[i])
                    await channel.send('c : Cancel')
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
                    state[guild.id] = ['waiting players', games[int(user_message) - 1]]
                    join_id[guild.id] = bot_message.id
                    now_playing = games[int(user_message) - 1]
            elif user_message == 'terminate' or user_message == 'end':
                for player in player_channels[guild.id]:
                    await player_channels[guild.id][player].delete()
                state[guild.id] = ['ready', '']

@client.event
async def on_raw_reaction_add(payload):
    channel_id = payload.channel_id
    guild_id = payload.guild_id
    user_id = payload.user_id
    channel = client.get_channel(channel_id)
    message_id = payload.message_id
    print(payload.member, payload.emoji)
    if payload.member == client.user:
        return
    player_channels_list = []
    for player in player_channels[guild_id]:
        player_channels_list.append(player_channels[guild_id][player])
        print(player_channels[guild_id][player].name)
    print(channel.name, )
    if str(channel) == 'boardgame':
        if str(payload.emoji) == '☑️':
            if state[guild_id][0] != 'playing':
                if message_id == join_id[guild_id] and payload.member not in players[guild_id]:
                    players[guild_id].append(payload.member)
                if len(players[guild_id]) >= min_players[state[guild_id][1]]:
                    if start_when_ready[guild_id]:
                        state[guild_id][0] = 'playing'
                        print(state)
        elif str(payload.emoji) == '▶️':
            if user_id == host_id[guild_id]:
                if len(players[guild_id]) >= min_players[state[guild_id][1]]:
                    state[guild_id][0] = 'playing'
                    print(state)
                else:
                    print('not enough players to play')
                    start_when_ready[guild_id] = True
        if state[guild_id][0] == 'playing':
            init(state[guild_id][1], guild_id)
            await channel.purge()
            print(deck[guild_id])
            guild = client.get_guild(guild_id)
            for player in players[guild_id]:
                channel = await create_player_text_channel(guild, player)
                player_channels[guild_id][player] = channel
                plays[guild_id][player] = []
            print(plays)
            for player in player_channels[guild_id]:
                message = await player_channels[guild_id][player].send('defuse')
            for i in range(4):
                for player in player_channels[guild_id]:
                    message = await player_channels[guild_id][player].send(deck[guild_id][0])
                    if 'card' not in deck[guild_id][0]:
                        await message.add_reaction('☑️')
                    deck[guild_id] = deck[guild_id][1:]
            for i in range(len(players[guild_id]) - 1):
                deck[guild_id].append('bomb')
            deck[guild_id].append('defuse')
            deck[guild_id].append('defuse')
            random.shuffle(deck[guild_id])
    elif channel in player_channels_list:
        print(str(payload.member).split('#')[0] + str(payload.member).split('#')[1], payload.member.name)
        if str(channel.name) == str(payload.member).split('#')[0].lower() + str(payload.member).split('#')[1]:
            if str(payload.emoji) == '☑️':
                plays[guild_id][payload.member].append(message_id)
                print(payload.member, plays[guild_id][payload.member])
        else:
            await main_channel[guild_id].send('server owner is now cheating')


async def create_player_text_channel(guild, user):
    print(guild, user)
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        user: discord.PermissionOverwrite(read_messages=True)
    }
    channel = await guild.create_text_channel(str(user).split('#')[0] + str(user).split('#')[1], overwrites=overwrites)
    return channel

import random

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
        if str(channel.name) == str(payload.member).split('#')[0] + str(payload.member).split('#')[1]:
            if str(payload.emoji) == '☑️':
                plays[guild_id].remove(message_id)
                print(payload.member, plays[guild_id][payload.member])

async def game_action(game):
    if game == 'exploding kittens':
        
        pass

client.run(TOKEN)
