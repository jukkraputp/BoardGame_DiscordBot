import random
import asyncio

import discord

# global vars
Client = None


def build_deck():
    deck = []
    for i in range(5):
        if i != 0:
            deck.append('attack')
            deck.append('skip')
            deck.append('shuffle')
            deck.append('favor')
            for i in range(5):
                deck.append('card' + str(i+1))
        deck.append('see the future')
        deck.append('nope')
    return deck


init_deck = build_deck()
card_pic = {
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
wait_time = 5
deck = []
discard_pile = {}
hands = {}
main_channel = None
emotable = []
player_turn = []
turn_message = None
double_turn = False
next_turn = 0
future_message = None
nope_able = {}
defuse = {}
nope_messages = {}
favor_target = None
player_alive = []
noped = False
pair = {}
triple = {}
five = {}
all_card_list = {}
all_card_type = ['attack', 'skip',
                 'see the future', 'shuffle', 'favor', 'defuse']
for i in range(1, 6):
    all_card_type.append('card' + str(i))


async def init(player_channels, players):
    global deck
    global nope_able
    global defuse
    global pair
    global triple
    global five
    global all_card_list

    deck = init_deck.copy()
    random.shuffle(deck)
    for player in players:
        channel = player_channels[player]
        hands[player] = []
        defuse[player] = []
        nope_able[player] = 0
        nope_messages[player] = []
        pair[player] = False
        triple[player] = False
        five[player] = {}
        all_card_list[player] = {}
        for i in range(5):
            all_card_list[player]['card' + str(i+1)] = 0
        await ADD_CARD(channel, player, 'defuse')
    for player in players:
        channel = player_channels[player]
        for i in range(4):
            card = deck[0]
            await ADD_CARD(channel, player, card)
            deck = deck[1:]
        # for testing
        test = False
        if test:
            for j in range(1):
                for i in range(5):
                    card = 'card' + str(i+1)
                    await ADD_CARD(channel, player, card)
            await check_special(player)
    for i in range(len(players) - 1):
        deck.append('bomb')
    deck.append('defuse')
    deck.append('defuse')
    random.shuffle(deck)


async def ExplodingKittens(client, guild, player_channels, players, channel):
    global Client
    global main_channel
    global player_turn
    global player_alive
    Client = client
    main_channel = channel
    player_alive = players
    await init(player_channels, players)
    player_turn = players.copy()
    random.shuffle(player_turn)

    winner = await asyncio.create_task(turn(player_turn[0], player_channels))
    return winner


async def print_turn(turn_list):
    for turn in turn_list:
        print(str(turn))


async def add_playable_card(card_message):
    global emotable
    card = card_message.content
    if card == 'attack' or card == 'skip' or card == 'shuffle' or card == 'see the future' or card == 'favor':
        await card_message.add_reaction('☑️')
        emotable.append(card_message)


async def turn(player, player_channels, messages=[]):
    global turn_message
    global emotable
    global player_turn
    global player_alive
    global next_turn
    global double_turn
    global pair
    global triple
    global five
    global all_card_list
    print(all_card_list[player])
    await print_turn(player_turn)
    channel = player_channels[player]
    if messages == []:
        await main_channel.send(player.mention + ' turn!')
        for card_message in hands[player]:
            messages.append(card_message)
            await add_playable_card(card_message)
        turn_message = await channel.send('draw')
        await turn_message.add_reaction('☑️')
        emotable.append(turn_message)
    if pair[player]:
        pair_message = await channel.send('pair')
        await pair_message.add_reaction('☑️')
        emotable.append(pair_message)
        messages.append(pair_message)
    if triple[player]:
        triple_message = await channel.send('three of a kind')
        await triple_message.add_reaction('☑️')
        emotable.append(triple_message)
        messages.append(triple_message)
    print(five[player].keys())
    if len(list(five[player].keys())) == 5:
        five_message = await channel.send('five different cards')
        await five_message.add_reaction('☑️')
        emotable.append(five_message)
        messages.append(five_message)
    if double_turn:
        player_turn = [player_turn[0]] + player_turn
        double_turn = False

    print('ACITON!')
    action, action_message = await asyncio.create_task(ACTION())
    special_action = ['pair', 'three of a kind', 'five different cards']
    normal_action = ['attack', 'skip', 'see the future', 'shuffle', 'favor']
    new_card_message = None
    special = False
    if action in special_action:
        special = True
    print(action)
    if action == 'attack':
        await ATTACK(player, player_channels)
    elif action == 'skip':
        await SKIP(player, player_channels)
    elif action == 'see the future':
        await SEE_THE_FUTURE(player, player_channels)
    elif action == 'shuffle':
        await SHUFFLE(player, player_channels)
    elif action == 'favor':
        await FAVOR(player, player_channels)
    elif action == 'draw':
        new_card_message = await DRAW(player, player_channels)
        if len(player_alive) == 1:
            return player_alive[0]
    elif special:
        if action == 'three of a kind':
            action = 'triple'
        elif action == 'five different cards':
            action = 'five'
        new_card_message = await SPECIAL(player, action, player_channels)
    if action in normal_action:
        hands[player].remove(action_message)
        await DISCARD(action)
    if new_card_message is not None:
        messages.append(new_card_message)
        await add_playable_card(new_card_message)
    if next_turn:
        if player_turn[0] != player_turn[1]:
            player_turn.append(player_turn[0])
        player_turn = player_turn[1:]
        next_turn -= 1
        for message in messages:
            try:
                await message.clear_reactions()
            except:
                pass
            if message in emotable:
                emotable.remove(message)
        messages = []
    else:
        messages.remove(action_message)
    await action_message.delete()
    try:
        await pair_message.delete()
    except:
        pass
    try:
        await triple_message.delete()
    except:
        pass
    try:
        await five_message.delete()
    except:
        pass
    return await asyncio.create_task(turn(player_turn[0], player_channels, messages))


async def ACTION():
    global turn_message
    try:
        print('wait reaction')
        reaction, user = await Client.wait_for('reaction_add', timeout=60, check=is_player_turn_reaction)
        print(str(user), str(reaction))
    except asyncio.TimeoutError:
        return 'draw', turn_message
    else:
        message = reaction.message
        return message.content, message


def is_emotable(reaction, user):
    message = reaction.message
    return message in emotable


def is_player_turn_reaction(reaction, user):
    if user == Client.user:
        return False
    global player_turn
    print(str(user), str(player_turn[0]))
    return user == player_turn[0] and is_emotable(reaction, user)


def is_got_bomb(m):
    try:
        float(m.content)
    except ValueError:
        return False
    else:
        return m.author == player_turn[0]


async def WAIT_PLACING_BOMB():
    try:
        message = await Client.wait_for('message', timeout=60, check=is_got_bomb)
        index = int(message.content)
    except asyncio.TimeoutError:
        return -1
    else:
        return index


async def DRAW(player, player_channels):
    global next_turn
    global player_turn
    global deck
    global all_card_list
    global pair
    global triple
    await main_channel.send('draw' + '!')
    card = deck[0]
    deck = deck[1:]
    if card == 'bomb':
        await main_channel.send(player.mention + ' got a bomb!')
        if len(defuse[player]) == 0:
            await main_channel.send(player.mention + ' doesn\'t has a defuse\n' + '😵')
            player_turn.remove(player)
            player_alive.remove(player)
            await DISCARD(card)
            for hand in hands[player]:
                await DISCARD(hand.content)
        else:
            await main_channel.send(player.mention + ' has a defuse\n' + 'please enter number between -1 and 99 to put a bomb back to deck\n(0 = top of deck, -1 = bottom of deck)')
            print('bomb')
            index = await asyncio.create_task(WAIT_PLACING_BOMB())
            print('bomb replacing at', index)
            if index >= len(deck):
                index = -1
            if index == -1:
                deck = deck + ['bomb']
            else:
                deck = deck[:index] + \
                    ['bomb'] + deck[index:]
            defuse_message = defuse[player].pop()
            await defuse_message.delete()
            for card in hands[player]:
                if str(card.content) == 'defuse':
                    hands[player].remove(card)
                    break
        await DISCARD('defuse')
    else:
        await ADD_CARD(player_channels[player], player, card)
    next_turn += 1


async def WAIT_FOR_NOPE():
    global noped
    while(True):
        try:
            reaction, user = await Client.wait_for('reaction_add', timeout=wait_time, check=check)
            nope_user = user
            print(str(nope_user) + ' use nope')
            pass
        except asyncio.TimeoutError:
            break
        else:
            await DISCARD('nope')
            message = await main_channel.send(nope_user.mention + ' NOPE!')
            await message.add_reaction('🚫')
            nope_message = nope_messages[nope_user].pop()
            hands[nope_user].remove(nope_message)
            await nope_message.delete()
            if noped == False:
                noped = True
            elif noped == True:
                noped = False


def check(reaction, user):
    if user != Client.user:
        return len(nope_messages[user]) > 0 and str(reaction.emoji) == '🚫'
    return False


async def SEE_THE_FUTURE(player, player_channels):
    global future_message
    global noped
    action_message = await main_channel.send('see the future' + '!')
    await action_message.add_reaction('🚫')
    if nope_able[player]:
        await WAIT_FOR_NOPE()
        if noped:
            print('get Noped')
            noped = False
            await action_message.reply('Failed!')
            return
    await action_message.reply('Successful!')
    message = '```'
    for i in range(3):
        message += '\n' + str(i+1) + ' : ' + deck[i]
    message += '```'
    channel = player_channels[player]
    future_message = await channel.send(message)


async def SHUFFLE(player, player_channels):
    global noped
    action_message = await main_channel.send('shuffle' + '!')
    await action_message.add_reaction('🚫')
    if nope_able[player]:
        await WAIT_FOR_NOPE()
        if noped:
            print('get Noped')
            noped = False
            await action_message.reply('Failed!')
            return
    await action_message.reply('Successful!')
    random.shuffle(deck)


def is_player_turn_message(message):
    return message.author == player_turn[0] and is_main_channel(message)


def is_main_channel(message):
    return message.channel == main_channel


async def WAIT_SELECT_FAVOR_TARGET(targets):
    try:
        message = await Client.wait_for('message', timeout=60, check=is_player_turn_message)
    except asyncio.TimeoutError:
        pass
    else:
        index = int(message.content)
        return targets[index]


def is_favor_target(reaction, user):
    return str(reaction) == '🃏'


async def WAIT_SELECT_FAVOR_CARD():
    try:
        reaction, user = await Client.wait_for('reaction_add', timeout=60, check=is_favor_target)
    except asyncio.TimeoutError:
        return None
    else:
        message = reaction.message
        return message


async def FAVOR(player, player_channels):
    global noped
    await main_channel.send('favor' + '!')

    FAVOR_TARGET_message = '```'
    order = 0
    targets = []
    for member in player_alive:
        if member != player:
            targets.append(member)
            FAVOR_TARGET_message += '\n' + str(order) + ' : ' + str(member)
            order += 1
    FAVOR_TARGET_message += '```'
    await main_channel.send(FAVOR_TARGET_message)
    target = await asyncio.create_task(WAIT_SELECT_TARGET(targets))
    action_message = await main_channel.send(target.mention + '!')
    await action_message.add_reaction('🚫')
    if nope_able[player]:
        await WAIT_FOR_NOPE()
        if noped:
            print('get Noped')
            noped = False
            await action_message.reply('Failed!')
            return
    await action_message.reply('Successful!')
    target_channel = player_channels[target]
    messages = []
    for card_message in hands[target]:
        await card_message.add_reaction('🃏')
        emotable.append(card_message)
        messages.append(card_message)
    target_message = await asyncio.create_task(WAIT_SELECT_FAVOR_CARD())
    if target_message is None:
        target_message = hands[target][random.randint(
            0, len(hands[target]) - 1)]
    for message in messages:
        await message.clear_reaction('🃏')
        emotable.remove(message)
    favor_card = target_message.content
    await REMOVE_CARD(target_message, target, favor_card)
    await ADD_CARD(player_channels[player], player, favor_card)


async def SKIP(player, player_channels):
    global next_turn
    global turn_message
    global noped
    global emotable
    action_message = await main_channel.send('skip' + '!')
    await action_message.add_reaction('🚫')
    if nope_able[player]:
        await WAIT_FOR_NOPE()
        if noped:
            print('get Noped')
            noped = False
            await action_message.reply('Failed!')
    await action_message.reply('Successful!')
    next_turn += 1
    emotable.remove(turn_message)
    await turn_message.delete()


async def ATTACK(player, player_channels):
    global next_turn
    global double_turn
    global turn_message
    global noped
    global emotable
    action_message = await main_channel.send('attack ' + player_turn[1].mention + '!')
    await action_message.add_reaction('🚫')
    if nope_able[player]:
        await WAIT_FOR_NOPE()
        if noped:
            print('get Noped')
            noped = False
            await action_message.reply('Failed!')
            return
    await action_message.reply('Successful!')
    double_turn = True
    next_turn += 1
    emotable.remove(turn_message)
    await turn_message.delete()


# \/ special actions ----------------------------------------------------------------


async def SPECIAL(player, special, player_channels):
    global five
    global all_card_list
    global noped
    action_message = await main_channel.send(special.upper() + '!')
    channel = player_channels[player]
    card_list = []
    if special == 'pair':
        for card in all_card_list[player]:
            if all_card_list[player][card] >= 2:
                card_list.append(card)
        await PAIR(player, channel, card_list, action_message)
    elif special == 'triple':
        for card in all_card_list[player]:
            if all_card_list[player][card] >= 3:
                card_list.append(card)
        await TRIPLE(player, channel, card_list, action_message)
    elif special == 'five':
        await action_message.add_reaction('🚫')
        card_list = list(five[player].keys())
        for card in card_list:
            for hand in hands[player]:
                if hand.content == card:
                    await REMOVE_CARD(hand, player, card)
                    break
            await DISCARD(card)
        if nope_able[player]:
            await WAIT_FOR_NOPE()
            if noped:
                print('get Noped')
                noped = False
                await action_message.reply('Failed!')
                return
        await action_message.reply('Successful!')
        await FIVE(player, channel)


def is_player_turn_reaction_special(reaction, user):
    return user == player_turn[0] and str(reaction.emoji) == '❌'


async def WAIT_SPECIAL():
    try:
        reaction, user = await Client.wait_for('reaction_add', timeout=999, check=is_player_turn_reaction_special)
    except asyncio.TimeoutError:
        return None
    else:
        return reaction.message


def is_player_turn_message(m):
    return m.author == player_turn[0] and m.channel == main_channel


async def WAIT_SELECT_TARGET(targets):
    try:
        message = await Client.wait_for('message', check=is_player_turn_message)
    except asyncio.TimeoutError:
        return targets[0]
    else:
        index = int(message.content)
        if index >= 0 and index < len(targets):
            return targets[index]


async def PAIR(player, channel, card_list, action_message):
    global all_card_list
    global noped
    messages = []
    for card in card_list:
        message = await channel.send(card)
        await message.add_reaction('❌')
        messages.append(message)
    card_message = await asyncio.create_task(WAIT_SPECIAL())
    for message in messages:
        await message.delete()
    if card_message is None:
        card = card_list[random.randint(0, len(card_list))]
    else:
        card = card_message.content
    all_card_list[player][card] -= 2
    await check_special(player)
    await DISCARD(card, 2)
    counter = 0
    for hand in hands[player].copy():
        if hand.content == card:
            counter += 1
            hands[player].remove(hand)
            await hand.delete()
        if counter == 2:
            break
    PAIR_TARGET_MESSAGE = '```Select your target'
    order = 0
    targets = []
    players = player_alive
    for member in players:
        if member != player:
            targets.append(member)
            PAIR_TARGET_MESSAGE += '\n' + str(order) + ' : ' + str(member)
            order += 1
    PAIR_TARGET_MESSAGE += '```'
    await main_channel.send(PAIR_TARGET_MESSAGE)
    target = await asyncio.create_task(WAIT_SELECT_TARGET(targets))
    wait_nope_message = await main_channel.send(target.mention + '!')
    await wait_nope_message.add_reaction('🚫')
    if nope_able[player]:
        await WAIT_FOR_NOPE()
        if noped:
            print('get Noped')
            noped = False
            await action_message.reply('Failed!')
            return
    await action_message.reply('Successful!')
    index = random.randint(0, len(hands[target]))
    target_message = hands[target][index]
    card = target_message.content
    await REMOVE_CARD(target_message, target, card)
    await ADD_CARD(channel, player, card)


async def WAIT_SELECT_TYPE():
    try:
        message = await Client.wait_for('message', timeout=60, check=is_player_turn_message)
    except asyncio.TimeoutError:
        return random.randint(1, len(all_card_type))
    else:
        return int(message.content)


async def TRIPLE(player, channel, card_list, action_message):
    global all_card_list
    global noped
    global hands
    messages = []
    for card in card_list:
        message = await channel.send(card)
        await message.add_reaction('❌')
        messages.append(message)
    card_message = await asyncio.create_task(WAIT_SPECIAL())
    for message in messages:
        await message.delete()
    card = card_message.content
    all_card_list[player][card] -= 3
    await check_special(player)
    await DISCARD(card, 3)
    counter = 0
    for hand in hands[player].copy():
        if hand.content == card:
            counter += 1
            hands[player].remove(hand)
            await hand.delete()
        if counter == 3:
            break
    TRIPLE_TARGET_MESSAGE = '```Select your target'
    order = 0
    targets = []
    players = player_alive
    for member in players:
        if member != player:
            targets.append(member)
            TRIPLE_TARGET_MESSAGE += '\n' + str(order) + ' : ' + str(member)
            order += 1
    TRIPLE_TARGET_MESSAGE += '```'
    await main_channel.send(TRIPLE_TARGET_MESSAGE)
    target = await asyncio.create_task(WAIT_SELECT_TARGET(targets))
    wait_nope_message = await main_channel.send(target.mention + '!')
    await wait_nope_message.add_reaction('🚫')
    if nope_able[player]:
        await WAIT_FOR_NOPE()
        if noped:
            print('get Noped')
            noped = False
            await action_message.reply('Failed!')
            return
    await action_message.reply('Successful!')
    CARD_TYPE_MESSAGE = '```Declare card name'
    order = 1
    for card in all_card_type:
        CARD_TYPE_MESSAGE += '\n' + str(order) + ' : ' + card
        order += 1
    CARD_TYPE_MESSAGE += '```'
    await main_channel.send(CARD_TYPE_MESSAGE)
    index = await asyncio.create_task(WAIT_SELECT_TYPE())
    index -= 1
    card = all_card_type[index]
    await main_channel.send(card)
    do_have = False
    for hand_message in hands[target]:
        hand = hand_message.content
        if hand == card:
            do_have = True
            target_message = hand_message
            break
    if do_have:
        await main_channel.send('Got you!', target.mention)
        await REMOVE_CARD(target_message, target, card)
        await ADD_CARD(channel, player, card)
    else:
        await main_channel.send('Unlucky for you!', player.mention)


def check_select_card(m):
    return m.author == player_turn[0] and m.channel == main_channel and int(m.content) > 0 and int(m.content) <= len(discard_pile.keys())


async def WAIT_SELECT_CARD():
    global discard_pile
    try:
        message = await Client.wait_for('message', timeout=60, check=check_select_card)
    except asyncio.TimeoutError:
        return list(discard_pile.keys())[random.randint(0, len(discard_pile.keys())-1)]
    else:
        index = int(message.content)
        index -= 1
        return list(discard_pile.keys())[index]


async def FIVE(player, channel):
    FIVE_MESSAGE = '```Select card from discard pile'
    order = 1
    for card in discard_pile.keys():
        FIVE_MESSAGE += '\n' + str(order) + ' : ' + str(card)
        order += 1
    FIVE_MESSAGE += '```'
    await main_channel.send(FIVE_MESSAGE)
    print('selecting a card')
    card = await asyncio.create_task(WAIT_SELECT_CARD())
    print('select', card)
    await ADD_CARD(channel, player, card)
    discard_pile[card] -= 1
    if discard_pile[card] == 0:
        discard_pile.pop(card)

# -----------------------------------------------------------------------------


async def ADD_CARD(channel, player, card):
    global all_card_list
    global pair
    global triple
    add = 1
    if card == 'nope':
        add = 5
    elif card == 'defuse' or card == 'see the future' or card == 'shuffle' or card == 'favor' or card == 'skip' or card == 'bomb':
        add = 3
    elif card == 'attack':
        add = 4
    card_message = await channel.send(content=card, file=discord.File(card_pic[card] + str(random.randint(1, add)) + '.png'))
    if card == 'defuse':
        defuse[player].append(card_message)
    elif card == 'nope':
        temp = player_alive
        for user in temp:
            nope_able[user] += 1
        nope_messages[player].append(card_message)
    elif 'card' in card:
        all_card_list[player][card] += 1
        five[player][card] = True
        await check_special(player)
    hands[player].append(card_message)


async def REMOVE_CARD(message, player, card):
    global all_card_list
    if card == 'defuse':
        defuse[player].remove(message)
    elif card == 'nope':
        temp = player_alive
        for user in temp:
            nope_able[user] -= 1
        nope_messages[player].remove(message)
    elif 'card' in card:
        all_card_list[player][card] -= 1
        if card in five[player]:
            five[player].pop(card)
        await check_special(player)
    hands[player].remove(message)
    await message.delete()


async def DISCARD(card, n=1):
    for i in range(n):
        if card in discard_pile:
            discard_pile[card] += 1
        else:
            discard_pile[card] = 1


async def check_special(player):
    global all_card_list
    global pair
    global triple
    global five

    pair[player] = False
    triple[player] = False
    for card in all_card_list[player]:
        if all_card_list[player][card] >= 2:
            pair[player] = True
        if all_card_list[player][card] >= 3:
            triple[player] = True
        if all_card_list[player][card] == 0 and card in five[player]:
            five[player].pop(card)
