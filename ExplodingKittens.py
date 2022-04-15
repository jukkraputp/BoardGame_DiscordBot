import random
import time
import asyncio

import discord

game_state = [
    'playing',
    'favor',
    'bomb',
    'nope'
]
nope_user = None
card_pic = {
    'Exploding Kittens': {
        'nope': 'Assets/ExplodingKittens/Nope/',
        'skip': 'Assets/ExplodingKittens/Skip/',
        'attack': 'Assets/ExplodingKittens/Attack/',
        'favor': 'Assets/ExplodingKittens/Favor/',
        'see the future': 'Assets/ExplodingKittens/SeeTheFuture/',
        'shuffle': 'Assets/ExplodingKittens/Shuffle/',
        'defuse': 'Assets/ExplodingKittens/Defuse/',
        'bomb': 'Assets/ExplodingKittens/Bomb/',
        'card1': 'Assets/ExplodingKittens/Card1/',
        'card2': 'Assets/ExplodingKittens/Card2/',
        'card3': 'Assets/ExplodingKittens/Card3/',
        'card4': 'Assets/ExplodingKittens/Card4/',
        'card5': 'Assets/ExplodingKittens/Card5/',
    }
}
wait_time = 5


async def ExplodingKittens(players,
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
                           discard_pile,
                           payload=None, guild_id=None, channel=None, message_id=None,
                           GAME_ACTION=False, user=None,
                           pair=False, triple=False, five=False, container=[]):

    global CLIENT
    CLIENT = client
    global PLAYERS
    PLAYERS = players
    global PLAYER_CHANNELS
    PLAYER_CHANNELS = player_channels
    global PLAYS
    PLAYS = plays
    global HANDS
    HANDS = hands
    global Favor
    Favor = favor
    global FAVOR_USER
    FAVOR_USER = favor_user
    global FAVOR_TARGET
    FAVOR_TARGET = favor_target
    global FAVOR_TARGET_LIST
    FAVOR_TARGET_LIST = favor_target_list
    global STATE
    STATE = state
    global MAIN_CHANNEL
    MAIN_CHANNEL = main_channel
    global TURN_MESSAGE
    TURN_MESSAGE = turn_message
    global DECK
    DECK = deck
    global DEFUSE
    DEFUSE = defuse
    global DOUBLE_TURN
    DOUBLE_TURN = double_turn
    global NEXT_TURN
    NEXT_TURN = next_turn
    global PLAYER_TURN
    PLAYER_TURN = player_turn
    global FUTURE_MESSAGE
    FUTURE_MESSAGE = future_message
    global NOPE_ABLE
    NOPE_ABLE = nope_able
    global NOPE_MESSAGES
    NOPE_MESSAGES = nope_messages
    global GUILD
    GUILD = CLIENT.get_guild(guild_id)
    special = False
    global DISCARD_PILE
    DISCARD_PILE = discard_pile
    if pair:
        special = 'pair'
    elif triple:
        special = 'triple'
    elif five:
        special = 'five'
    if special:
        await SPECIAL(GUILD, user, special, container)
    elif GAME_ACTION:
        await game_action(GUILD, 'Exploding Kittens', user)
    else:
        await GAME(payload, guild_id, channel, message_id)
    return (players,
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
            discard_pile
            )


async def GAME(payload, guild_id, channel, message_id):
    if str(channel.name) == str(payload.member).split('#')[0].lower() + str(payload.member).split('#')[1]:
        if str(payload.emoji) == '☑️':
            PLAYS[guild_id][payload.member].append(message_id)
        if str(payload.emoji) == '🃏':
            print(f'{payload.member} got favor!')
            sender_channel = PLAYER_CHANNELS[guild_id][payload.member]
            sender_message = await sender_channel.fetch_message(message_id)
            card = str(sender_message.content)
            favor_channel = PLAYER_CHANNELS[guild_id][FAVOR_USER[guild_id]]
            await ADD_CARD(CLIENT.get_guild(guild_id), favor_channel, payload.member, card)
            HANDS[guild_id][payload.member].remove(sender_message)
            for card_message in HANDS[guild_id][payload.member]:
                await card_message.remove_reaction('🃏', CLIENT.user)
            await sender_message.delete()
            Favor[guild_id] = False
            temp_FAVOR_USER = FAVOR_USER[guild_id]
            FAVOR_USER[guild_id] = None
            FAVOR_TARGET[guild_id] = None
            FAVOR_TARGET_LIST[guild_id] = []
            STATE[guild_id][0] = game_state[0]
            await game_action(CLIENT.get_guild(guild_id), 'Exploding Kittens', temp_FAVOR_USER)
    else:
        await MAIN_CHANNEL[guild_id].send('server owner is now cheating')
    await game_action(CLIENT.get_guild(guild_id), STATE[guild_id][1], payload.member)

    return


async def game_action(guild, game, player, special=False):
    print(guild, game, player)
    global Favor
    global NEXT_TURN
    global DOUBLE_TURN
    global PLAYER_TURN
    global FUTURE_MESSAGE
    if Favor[guild.id]:
        Favor[guild.id] = False
        target_HANDS = HANDS[guild.id][FAVOR_TARGET[guild.id]]
        if len(target_HANDS) == 0:
            Favor[guild.id] = False
            temp_FAVOR_USER = FAVOR_USER[guild.id].copy()
            FAVOR_USER[guild.id] = None
            FAVOR_TARGET[guild.id] = None
            FAVOR_TARGET_LIST[guild.id] = []
            await game_action(guild, game, temp_FAVOR_USER)
        else:
            for card_message in target_HANDS:
                await card_message.add_reaction('🃏')
    elif player == PLAYER_TURN[guild.id][0]:
        if game == 'Exploding Kittens':
            if len(PLAYS[guild.id][player]) != 0:
                message_id = PLAYS[guild.id][player][0]
                PLAYS[guild.id][player] = PLAYS[guild.id][player][1:]
                channel = PLAYER_CHANNELS[guild.id][player]
                action_container = await channel.fetch_message(message_id)
                action = action_container.content
                print(player.name, action)
                if action == 'attack':
                    await ATTACK(guild, game, player, channel)
                elif action == 'skip':
                    await SKIP(guild, game, player, channel)
                elif action == 'see the future':
                    await SEE_THE_FUTURE(guild, game, player, channel)
                elif action == 'shuffle':
                    await SHUFFLE(guild, game, player, channel)
                elif action == 'favor':
                    await FAVOR(guild, game, player, channel)
                    HANDS[guild.id][player].remove(action_container)
                    await action_container.delete()
                    return
                elif action == 'draw':
                    await DRAW(guild, game, player, channel)
                if action != 'draw':
                    HANDS[guild.id][player].remove(action_container)
                    await DISCARD(guild, action)
                await action_container.delete()
            if NEXT_TURN[guild.id]:
                if FUTURE_MESSAGE[guild.id] != None:
                    await FUTURE_MESSAGE[guild.id].delete()
                    FUTURE_MESSAGE[guild.id] = None
                NEXT_TURN[guild.id] = False
                if DOUBLE_TURN[guild.id] > 0 and action != 'attack':
                    DOUBLE_TURN[guild.id] -= 1
                else:
                    PLAYER_TURN[guild.id].append(player)
                    PLAYER_TURN[guild.id] = PLAYER_TURN[guild.id][1:]
                await MAIN_CHANNEL[guild.id].send(PLAYER_TURN[guild.id][0].mention + ' turn!')
                print(f'{PLAYER_TURN[guild.id][0].name} turn!')
                message = await PLAYER_CHANNELS[guild.id][PLAYER_TURN[guild.id][0]].send('draw')
                await message.add_reaction('☑️')
                TURN_MESSAGE[guild.id] = message
            if len(PLAYS[guild.id][PLAYER_TURN[guild.id][0]]) != 0:
                await game_action(guild, game, PLAYER_TURN[guild.id][0])


async def DRAW(guild, game, player, channel):
    global NEXT_TURN
    global PLAYER_TURN
    if game == 'Exploding Kittens':
        await MAIN_CHANNEL[guild.id].send('draw' + '!')
        card = DECK[guild.id][0]
        DECK[guild.id] = DECK[guild.id][1:]
        if card == 'bomb':
            await MAIN_CHANNEL[guild.id].send(player.mention + ' got a bomb!')
            if len(DEFUSE[guild.id][player]) == 0:
                await MAIN_CHANNEL[guild.id].send(player.mention + ' doesn\'t has a defuse\n' + '😵')
                PLAYER_TURN[guild.id].remove(player)
                await DISCARD(guild, card)
            else:
                await MAIN_CHANNEL[guild.id].send(player.mention + ' has a defuse\n' + 'please enter number between -1 and 99 to put a bomb back to DECK (0 = top of DECK, -1 = bottom of DECK)')
                STATE[guild.id][0] = game_state[2]
                defuse_message = DEFUSE[guild.id][player].pop()
                await defuse_message.delete()
                for card in HANDS[guild.id][player]:
                    if str(card.content) == 'defuse':
                        HANDS[guild.id][player].remove(card)
                        break
            DISCARD(guild, 'defuse')
        else:
            await ADD_CARD(guild, channel, player, card)
        NEXT_TURN[guild.id] = True


async def WAIT_FOR_NOPE(guild):
    while(True):
        try:
            reaction, user = await CLIENT.wait_for('reaction_add', timeout=wait_time, check=check)
            nope_user = user
            print(str(nope_user) + ' use nope')
            pass
        except asyncio.TimeoutError:
            break
        else:
            message = await MAIN_CHANNEL[guild.id].send(nope_user.mention + ' NOPE!')
            await message.add_reaction('🚫')
            nope_message = NOPE_MESSAGES[guild.id][nope_user].pop()
            HANDS[guild.id][nope_user].remove(nope_message)
            await nope_message.delete()
            if STATE[guild.id][0] == game_state[3]:
                STATE[guild.id][0] = game_state[0]
            elif STATE[guild.id][0] == game_state[0]:
                STATE[guild.id][0] = game_state[3]


def check(reaction, user):
    if user != CLIENT.user:
        return len(NOPE_MESSAGES[GUILD.id][user]) > 0 and str(reaction.emoji) == '🚫'
    return False


async def SEE_THE_FUTURE(guild, game, player, channel):
    global FUTURE_MESSAGE
    global nope_user

    if game == 'Exploding Kittens':
        action_message = await MAIN_CHANNEL[guild.id].send('see the future' + '!')
        await action_message.add_reaction('🚫')
        if NOPE_ABLE[guild.id]:
            await WAIT_FOR_NOPE(guild)
            if STATE[guild.id][0] == game_state[3]:
                print('get Noped')
                STATE[guild.id][0] = game_state[0]
                await action_message.reply('Failed!')
                return
        await action_message.reply('Successful!')
        message = '```'
        for i in range(3):
            message += '\n' + str(i+1) + ' : ' + DECK[guild.id][i]
        message += '```'
        FUTURE_MESSAGE[guild.id] = await channel.send(message)


async def SHUFFLE(guild, game, player, channel):
    global nope_user

    if game == 'Exploding Kittens':
        action_message = await MAIN_CHANNEL[guild.id].send('shuffle' + '!')
        await action_message.add_reaction('🚫')
        if NOPE_ABLE[guild.id]:
            await WAIT_FOR_NOPE(guild)
            if STATE[guild.id][0] == game_state[3]:
                print('get Noped')
                STATE[guild.id][0] = game_state[0]
                await action_message.reply('Failed!')
                return
        await action_message.reply('Successful!')
        random.shuffle(DECK[guild.id])
        return


async def FAVOR(guild, game, player, channel):
    global Favor
    global nope_user

    if game == 'Exploding Kittens':
        action_message = await MAIN_CHANNEL[guild.id].send('favor' + '!')
        await action_message.add_reaction('🚫')
        if NOPE_ABLE[guild.id]:
            await WAIT_FOR_NOPE(guild)
            if STATE[guild.id][0] == game_state[3]:
                print('get Noped')
                STATE[guild.id][0] = game_state[0]
                await action_message.reply('Failed!')
                return
        await action_message.reply('Successful!')
        Favor[guild.id] = True
        FAVOR_USER[guild.id] = player
        STATE[guild.id][0] = game_state[1]
        FAVOR_TARGET_message = '```'
        order = 0
        for member in PLAYERS[guild.id]:
            if member != player:
                FAVOR_TARGET_message += '\n' + str(order) + ' : ' + str(member)
                order += 1
                FAVOR_TARGET_LIST[guild.id].append(member)
        FAVOR_TARGET_message += '```'
        await MAIN_CHANNEL[guild.id].send(FAVOR_TARGET_message)


async def SKIP(guild, game, player, channel):
    global NEXT_TURN
    global nope_user

    if game == 'Exploding Kittens':
        action_message = await MAIN_CHANNEL[guild.id].send('skip' + '!')
        await action_message.add_reaction('🚫')
        if NOPE_ABLE[guild.id]:
            await WAIT_FOR_NOPE(guild)
            if STATE[guild.id][0] == game_state[3]:
                print('get Noped')
                STATE[guild.id][0] = game_state[0]
                await action_message.reply('Failed!')
                return
        await action_message.reply('Successful!')
        NEXT_TURN[guild.id] = True
        await TURN_MESSAGE[guild.id].delete()


async def ATTACK(guild, game, player, channel):
    global NEXT_TURN
    global DOUBLE_TURN
    global nope_user

    if game == 'Exploding Kittens':
        action_message = await MAIN_CHANNEL[guild.id].send('attack ' + PLAYER_TURN[guild.id][1].mention + '!')
        await action_message.add_reaction('🚫')
        if NOPE_ABLE[guild.id]:
            await WAIT_FOR_NOPE(guild)
            if STATE[guild.id][0] == game_state[3]:
                print('get Noped')
                STATE[guild.id][0] = game_state[0]
                await action_message.reply('Failed!')
                return
        await action_message.reply('Successful!')
        DOUBLE_TURN[guild.id] += 1
        NEXT_TURN[guild.id] = True
        await TURN_MESSAGE[guild.id].delete()


# \/ special actions ----------------------------------------------------------------


async def SPECIAL(guild, player, special, card_list):
    action_message = await MAIN_CHANNEL[guild.id].send(special.upper() + '!')
    await action_message.add_reaction('🚫')
    if NOPE_ABLE[guild.id]:
        await WAIT_FOR_NOPE(guild)
        if STATE[guild.id][0] == game_state[3]:
            print('get Noped')
            STATE[guild.id][0] = game_state[0]
            await action_message.reply('Failed!')
            return
    await action_message.reply('Successful!')
    channel = PLAYER_CHANNELS[guild.id][player]
    if special == 'pair':
        await PAIR(guild, player, channel, card_list)
    elif special == 'triple':
        await TRIPLE(guild, player, channel, card_list)
    elif special == 'five':
        await FIVE(guild, player, channel, card_list)


def is_player_turn_reaction(reaction, user, message):
    return user == PLAYER_TURN[GUILD.id][0]


async def WAIT_SPECIAL():
    try:
        reaction, user = await CLIENT.wait_for('reaction_add', timeout=wait_time, check=is_player_turn_reaction)
        return reaction.message
    except asyncio.TimeoutError:
        return None


def is_player_turn_message(m):
    return m.author == PLAYER_TURN[GUILD.id][0] and m.channel == MAIN_CHANNEL[GUILD.id]


async def WAIT_SELECT_TARGET(targets):
    message = await CLIENT.wait_for('message', check=is_player_turn_message)
    index = int(message.content)
    if index >= 0 and index < len(targets):
        return targets[index]


async def PAIR(guild, player, channel, card_list):
    messages = []
    for card in card_list:
        message = await channel.send(card)
        await message.add_reaction('☑️')
        messages.append(message)
    card_message = await WAIT_SPECIAL()
    if card_message is None:
        card_message = messages[0]
    card = card_message.content
    counter = 0
    for hand in HANDS[guild.id][player].copy():
        if hand.content == card:
            counter += 1
            HANDS[guild.id][player].remove(hand)
        if counter == 2:
            break
    PAIR_TARGET_MESSAGE = '```'
    order = 0
    targets = []
    for member in PLAYERS[guild.id]:
        if member != player:
            targets.append(member)
            PAIR_TARGET_MESSAGE += '\n' + str(order) + ' : ' + str(member)
            order += 1
    PAIR_TARGET_MESSAGE += '```'
    await MAIN_CHANNEL[guild.id].send(PAIR_TARGET_MESSAGE)
    target = await WAIT_SELECT_TARGET(targets)
    for message in messages:
        await message.delete()
    index = random.randint(0, len(HANDS[guild.id][target]))
    target_message = HANDS[guild.id][target][index]
    card = target_message.content
    await REMOVE_CARD(guild, target_message, target, card)
    await ADD_CARD(guild, channel, player, card)


async def TRIPLE(guild, player, channel, card_list):
    messages = []
    for card in card_list:
        message = await channel.send(card)
        await message.add_reaction('☑️')
        messages.append(message)
    card_message = await WAIT_SPECIAL()
    if card_message is None:
        card_message = messages[0]
    card = card_message.content
    counter = 0
    for hand in HANDS[guild.id][player].copy():
        if hand.content == card:
            counter += 1
            HANDS[guild.id][player].remove(hand)
        if counter == 3:
            break
    TRIPLE_TARGET_MESSAGE = '```'
    order = 0
    targets = []
    for member in PLAYERS[guild.id]:
        if member != player:
            targets.append(member)
            TRIPLE_TARGET_MESSAGE += '\n' + str(order) + ' : ' + str(member)
            order += 1
    TRIPLE_TARGET_MESSAGE += '```'
    await MAIN_CHANNEL[guild.id].send(TRIPLE_TARGET_MESSAGE)
    target = await WAIT_SELECT_TARGET(targets)
    for message in messages:
        await message.delete()
    index = random.randint(0, len(HANDS[guild.id][target]))
    target_message = HANDS[guild.id][target][index]
    card = target_message.content
    await REMOVE_CARD(guild, target_message, target, card)
    await ADD_CARD(guild, channel, player, card)


async def WAIT_SELECT_CARD():
    message = await CLIENT.wait_for('message', check=is_player_turn_message)
    index = message.content
    return DISCARD_PILE[GUILD.id].unique()[index]


async def FIVE(guild, player, channel, card_list):
    for card in card_list:
        for hand in HANDS[guild.id][player].copy():
            if hand.content == card:
                HANDS[guild.id][player].remove(hand)
                await hand.delete()
                break
    card = await WAIT_SELECT_CARD()
    await ADD_CARD(guild, channel, player, card)
    for i in range(len(DISCARD_PILE[GUILD.id])):
        card_name = DISCARD_PILE[GUILD.id][i]
        if card_name == card:
            DISCARD_PILE[GUILD.id].pop(i)
            break

# -----------------------------------------------------------------------------


async def ADD_CARD(guild, channel, player, card):
    add = 1
    if card == 'nope':
        add = 5
    elif card == 'defuse' or card == 'see the future' or card == 'shuffle' or card == 'favor' or card == 'skip' or card == 'bomb':
        add = 3
    elif card == 'attack':
        add = 4
    game = 'Exploding Kittens'
    card_message = await channel.send(content=card, file=discord.File(card_pic[game][card] + str(random.randint(1, add)) + '.png'))
    if 'card' not in card and card != 'defuse' and card != 'nope':
        await card_message.add_reaction('☑️')
    elif card == 'defuse':
        DEFUSE[guild.id][player].append(card_message)
    elif card == 'nope':
        NOPE_ABLE[guild.id] += 1
        NOPE_MESSAGES[guild.id][player].append(card_message)
    HANDS[guild.id][player].append(card_message)


async def REMOVE_CARD(guild, message, player, card):
    if card == 'defuse':
        DEFUSE[guild.id][player].remove(message)
    elif card == 'nope':
        NOPE_ABLE[guild.id] -= 1
        NOPE_MESSAGES[guild.id][player].remove(message)
    HANDS[guild.id][player].remove(message)
    await message.delete()


async def DISCARD(guild, card):
    DISCARD_PILE[guild.id].append(card)
