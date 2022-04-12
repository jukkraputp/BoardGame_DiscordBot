import os

import discord
from discord.ext import commands
from dotenv import load_dotenv
import random

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
games = ['Exploding Kittens']
min_players = {
    'Exploding Kittens': 2
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
skip_turn = {}
favor = {}


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
        join_id[guild.id] = None
        host_id[guild.id] = None
        state[guild.id] = ['ready', None]
        start_when_ready[guild.id] = False
        plays[guild.id] = {}
        favor_target_list[guild.id] = []
        now_playing[guild.id] = None
        favor_user[guild.id] = None
        player_turn[guild.id] = []
        hands[guild.id] = {}
        double_turn[guild.id] = False
        skip_turn[guild.id] = False
        favor[guild.id] = False


@client.event
async def on_message(message):
    username = str(message.author).split('#')[0]
    user_message = str(message.content)
    channel = message.channel
    guild = message.guild
    if str(message.author) != 'ProjectBeta#6332':
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
                    state[guild.id] = ['waiting players',
                                       games[int(user_message) - 1]]
                    join_id[guild.id] = bot_message.id
                    now_playing[guild.id] = games[int(user_message) - 1]
            elif state[guild.id][0] == 'select favor target' and message.author == favor_user[guild.id]:
                await game_action(guild, now_playing[guild.id], message.author, favor_target=favor_target_list[int(user_message) - 1])
            elif user_message == 'terminate' or user_message == 'end':
                for player in player_channels[guild.id]:
                    await player_channels[guild.id][player].delete()
                state[guild.id] = ['ready', '']


@client.event
async def on_raw_reaction_add(payload):
    global player_turn
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
                if len(players[guild_id]) >= min_players[state[guild_id][1]]:
                    state[guild_id][0] = 'init'
                    print(state)
                else:
                    print('not enough players to play')
                    start_when_ready[guild_id] = True
        if state[guild_id][0] == 'init':
            state[guild_id][0] = 'playing'
            if state[guild_id][1] == 'Exploding Kittens':
                init(state[guild_id][1], guild_id)
                await channel.purge()
                print(deck[guild_id])
                guild = client.get_guild(guild_id)
                for player in players[guild_id]:
                    channel = await create_player_text_channel(guild, player)
                    player_channels[guild_id][player] = channel
                    plays[guild_id][player] = []
                for player in player_channels[guild_id]:
                    message = await player_channels[guild_id][player].send('defuse')
                for i in range(4):
                    for player in player_channels[guild_id]:
                        message = await player_channels[guild_id][player].send(deck[guild_id][0])
                        if 'card' not in deck[guild_id][0] and deck[guild_id][0] != 'nope':
                            await message.add_reaction('☑️')
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
                await main_channel[guild_id].send(player_turn[guild_id][0].mention + ' turn!')
    elif channel in player_channels_list:
        if state[guild_id][1] == games[0]:
            print(str(payload.member).split('#')[0].lower() + 
            str(payload.member).split('#')[1], 
            str(channel.name))
            if str(channel.name) == str(payload.member).split('#')[0].lower() + str(payload.member).split('#')[1]:
                if str(payload.emoji) == '☑️':
                    plays[guild_id][payload.member].append(message_id)
                    print(payload.member, plays[guild_id][payload.member])
            else:
                await main_channel[guild_id].send('server owner is now cheating')
            await game_action(client.get_guild(guild_id), state[guild_id][1], payload.member)



async def game_action(guild, game, player, favor_target=False):
    print(guild, player, game)
    global favor
    global skip_turn
    global double_turn
    global player_turn
    print('turn list')
    for i in range(len(player_turn[guild.id])):
        print(str(player_turn[guild.id][i]))
    print('---')
    if favor[guild.id]:
        pass
    print(str(player), str(player_turn[guild.id][0]))
    if player == player_turn[guild.id][0]:
        if game == games[0]:
            while(True):
                if len(plays[guild.id][player]) != 0:
                    if favor_target:
                        if len(hands[guild.id][favor_target]) != 0:
                            return
                    if not double_turn[guild.id]:
                        print('not double')
                        player_turn[guild.id].append(player)
                        player_turn[guild.id] = player_turn[guild.id][1:]
                        print('turn list')
                        for i in range(len(player_turn[guild.id])):
                            print(str(player_turn[guild.id][i]))
                        print('\n')
                    else:
                        double_turn[guild.id] = False
                    message_id = plays[guild.id][player][0]
                    plays[guild.id][player] = plays[guild.id][player][1:]
                    channel = player_channels[guild.id][player]
                    action_container = await channel.fetch_message(message_id)
                    action = action_container.content
                    print(action)
                    if action == 'attack':
                        double_turn[guild.id] = True
                        skip_turn[guild.id] = True
                    elif action == 'skip':
                        skip_turn[guild.id] = True
                    elif action == 'see the future':
                        future_message = (
                            '```' + deck[guild.id][0] +
                            '\n' + deck[guild.id][1] + 
                            '\n' + deck[guild.id][2] + '```')
                        future_message = await player_channels[guild.id][player].send(future_message)
                    elif action == 'favor':
                        favor = True
                        state[guild.id][0] = 'select favor target'
                        favor_target_message = '```'
                        order = 0
                        for member in players[guild.id]:
                            if member != player:
                                favor_target_message += '\n' + str(order) + ' : ' + str(member)
                                order += 1
                                favor_target_list.append(member)
                        member += '```'
                        await main_channel.send(favor_target_message)
                    elif action == 'draw':
                        await main_channel[guild.id].send(action + '!')
                        print(player_turn[guild.id], 'next turn!')
                        await main_channel[guild.id].send(player_turn[guild.id][0].mention + ' turn!')
                        message = await player_channels[guild.id][player_turn[guild.id][0]].send('draw')
                        await message.add_reaction('☑️')
                        await game_action(guild, game, player_turn[guild.id][0])
                    await action_container.delete()
                    break
                else:
                    break

async def create_player_text_channel(guild, user):
    print(guild, user)
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        user: discord.PermissionOverwrite(read_messages=True)
    }
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
