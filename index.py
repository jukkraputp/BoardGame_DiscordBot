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
nope_able_message = {}
temp_list = {}
favor_target = {}
turn_message = {}
future_message = {}


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
            main_channel_name[guild.id] = default_channel_name
            deck[guild.id] = []
            players[guild.id] = []
            player_channels[guild.id] = {}
            join_id[guild.id] = None
            host_id[guild.id] = None
            state[guild.id] = ['ready', None]
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
            nope_able_message[guild.id] = None
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
                    state[guild.id] = ['waiting players',
                                       games[int(user_message) - 1]]
                    join_id[guild.id] = bot_message.id
                    now_playing[guild.id] = games[int(user_message) - 1]
            elif user_message == 'terminate' or user_message == 'end':
                for player in player_channels[guild.id]:
                    await player_channels[guild.id][player].delete()
                state[guild.id] = ['ready', '']
            elif state[guild.id][0] == 'select favor target' and message.author == favor_user[guild.id] and int(user_message) - 1 < len(favor_target_list[guild.id]):
                favor_target[guild.id] = favor_target_list[guild.id][int(
                    user_message) - 1]
                [players,
                 player_channels,
                 plays, hands,
                 client,
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
                 future_message] = await ExplodingKittens(players,
                                                          player_channels,
                                                          plays, hands,
                                                          client,
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
    channel_id = payload.channel_id
    guild_id = payload.guild_id
    user_id = payload.user_id
    channel = client.get_channel(channel_id)
    message_id = payload.message_id
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
            state[guild_id][0] = 'playing'
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
                for player in player_channels[guild_id]:
                    message = await player_channels[guild_id][player].send('defuse')
                    hands[guild_id][player].append(message)
                    defuse[guild_id][player].append(message)
                for i in range(4):
                    for player in player_channels[guild_id]:
                        message = await player_channels[guild_id][player].send(deck[guild_id][0])
                        if 'card' not in deck[guild_id][0] and deck[guild_id][0] != 'nope':
                            await message.add_reaction('☑️')
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
            [players,
             player_channels,
             plays, hands,
             client,
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
             future_message] = await ExplodingKittens(players,
                                                      player_channels,
                                                      plays, hands,
                                                      client,
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
                                                      payload=payload, guild_id=guild_id, channel=channel, message_id=message_id)

""" async def ExplodingKittens(payload, guild_id, channel, message_id):
    print(str(payload.member).split('#')[0].lower() +
            str(payload.member).split('#')[1],
            str(channel.name))
    if str(channel.name) == str(payload.member).split('#')[0].lower() + str(payload.member).split('#')[1]:
        if str(payload.emoji) == '☑️':
            plays[guild_id][payload.member].append(message_id)
            print(payload.member, plays[guild_id][payload.member])
        if str(payload.emoji) == '🃏':
            print('got favor!')
            sender_channel = player_channels[guild_id][payload.member]
            sender_message = await sender_channel.fetch_message(message_id)
            card = str(sender_message.content)
            favor_channel = player_channels[guild_id][favor_user[guild_id]]
            card_message = await favor_channel.send(card)
            if 'card' not in card and card != 'defuse' and card != 'nope':
                await card_message.add_reaction('☑️')
            hands[guild_id][favor_user[guild_id]].append(card_message)
            hands[guild_id][payload.member].remove(sender_message)
            for card_message in hands[guild_id][payload.member]:
                await card_message.remove_reaction('🃏', client.user)
            await sender_message.delete()
            favor[guild_id] = False
            temp_favor_user = favor_user[guild_id]
            favor_user[guild_id] = None
            favor_target[guild_id] = None
            favor_target_list[guild_id] = []
            state[guild_id][0] = 'playing'
            await game_action(client.get_guild(guild_id), now_playing, temp_favor_user)
    else:
        await main_channel[guild_id].send('server owner is now cheating')
    await game_action(client.get_guild(guild_id), state[guild_id][1], payload.member)

    return """


""" async def game_action(guild, game, player):
    print(guild, player, game)
    global favor
    global next_turn
    global double_turn
    global player_turn
    if favor[guild.id]:
        favor[guild.id] = False
        target_hands = hands[guild.id][favor_target[guild.id]]
        if len(target_hands) == 0:
            favor[guild.id] = False
            temp_favor_user = favor_user[guild.id].copy()
            favor_user[guild.id] = None
            favor_target[guild.id] = None
            favor_target_list[guild.id] = []
            await game_action(guild, game, temp_favor_user)
        else:
            for card_message in target_hands:
                await card_message.add_reaction('🃏')
    elif player == player_turn[guild.id][0]:
        if game == games[0]:
            if len(plays[guild.id][player]) != 0:
                message_id = plays[guild.id][player][0]
                plays[guild.id][player] = plays[guild.id][player][1:]
                channel = player_channels[guild.id][player]
                action_container = await channel.fetch_message(message_id)
                action = action_container.content
                if action == 'attack':
                    await ExplodingKittens.ATTACK(guild, game, player, channel)
                elif action == 'skip':
                    await ExplodingKittens.SKIP(guild, game, player, channel)
                elif action == 'see the future':
                    await ExplodingKittens.SEE_THE_FUTURE(guild, game, player, channel)
                elif action == 'shuffle':
                    await ExplodingKittens.SHUFFLE(guild, game, player, channel)
                elif action == 'favor':
                    await ExplodingKittens.FAVOR(guild, game, player, channel)
                    hands[guild.id][player].remove(action_container)
                    await action_container.delete()
                    return
                elif action == 'draw':
                    await ExplodingKittens.DRAW(guild, game, player, channel)
                if action != 'draw':
                    hands[guild.id][player].remove(action_container)
                await action_container.delete()
            print(player_turn[guild.id][0],
                  next_turn[guild.id], double_turn[guild.id])
            if next_turn[guild.id]:
                if future_message[guild.id] != None:
                    await future_message[guild.id].delete()
                    future_message[guild.id] = None
                next_turn[guild.id] = False
                if double_turn[guild.id] > 0 and action != 'attack':
                    double_turn[guild.id] -= 1
                else:
                    player_turn[guild.id].append(player)
                    player_turn[guild.id] = player_turn[guild.id][1:]
                await main_channel[guild.id].send(player_turn[guild.id][0].mention + ' turn!')
                message = await player_channels[guild.id][player_turn[guild.id][0]].send('draw')
                await message.add_reaction('☑️')
                turn_message[guild.id] = message
            print(player_turn[guild.id][0],
                  next_turn[guild.id], double_turn[guild.id])
            if len(plays[guild.id][player_turn[guild.id][0]]) != 0:
                await game_action(guild, game, player_turn[guild.id][0]) """


""" async def DRAW(guild, game, player, channel):
    global next_turn
    global player_turn
    if game == games[0]:
        await main_channel[guild.id].send('draw' + '!')
        card = deck[guild.id][0]
        deck[guild.id] = deck[guild.id][1:]
        if card == 'bomb':
            await main_channel[guild.id].send(player.mention + ' got a bomb!')
            if 'defuse' not in hands[guild.id][player]:
                await main_channel[guild.id].send(player.mention + ' doesn\'t has a defuse\n' + '😵')
                player_turn[guild.id].remove(player)
            else:
                await main_channel[guild.id].send(player.mention + ' has a defuse\n' + 'please enter number between -1 and 99 to put a bomb back to deck (0 = top of deck, -1 = bottom of deck)')
                defuse[guild.id][player].pop()
                for card in hands[guild.id][player]:
                    if str(card.content) == 'defuse':
                        hands[guild.id][player].remove(card)
                        break
        else:
            card_message = await channel.send(card)
            if 'card' not in card and card != 'defuse' and card != 'nope':
                await card_message.add_reaction('☑️')
            hands[guild.id][player].append(card_message)
        next_turn[guild.id] = True


async def SEE_THE_FUTURE(guild, game, player, channel):
    global future_message
    if game == games[0]:
        action_message = await main_channel[guild.id].send('see the future' + '!')
        await action_message.add_reaction('🚫')
        message = '```'
        for i in range(3):
            message += '\n' + str(i+1) + ' : ' + deck[guild.id][i]
        message += '```'
        future_message[guild.id] = await channel.send(message)


async def SHUFFLE(guild, game, player, channel):
    if game == games[0]:
        random.shuffle(deck[guild.id])
        return


async def FAVOR(guild, game, player, channel):
    global favor
    if game == games[0]:
        action_message = await main_channel[guild.id].send('favor' + '!')
        await action_message.add_reaction('🚫')
        favor[guild.id] = True
        favor_user[guild.id] = player
        state[guild.id][0] = 'select favor target'
        favor_target_message = '```'
        order = 0
        for member in players[guild.id]:
            if member != player:
                favor_target_message += '\n' + str(order) + ' : ' + str(member)
                order += 1
                favor_target_list[guild.id].append(member)
        favor_target_message += '```'
        await main_channel[guild.id].send(favor_target_message)


async def SKIP(guild, game, player, channel):
    global next_turn
    if game == games[0]:
        action_message = await main_channel[guild.id].send('skip' + '!')
        await action_message.add_reaction('🚫')
        next_turn[guild.id] = True
        await turn_message[guild.id].delete()


async def ATTACK(guild, game, player, channel):
    global next_turn
    global double_turn
    if game == games[0]:
        action_message = await main_channel[guild.id].send('attack ' + player_turn[guild.id][1].mention + '!')
        await action_message.add_reaction('🚫')
        double_turn[guild.id] += 1
        next_turn[guild.id] = True
        await turn_message[guild.id].delete()


async def PAIR(guild, game, player, channel):
    if game == games[0]:
        return


async def THREE_OF_A_KIND(guild, game, player, channel):
    if game == games[0]:
        return


async def FIVE_UNIQUE(guild, game, player, channel):
    if game == games[0]:
        return """


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
