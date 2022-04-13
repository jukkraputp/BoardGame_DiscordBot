import random


async def ExplodingKittens(players,
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
                     payload=None, guild_id=None, channel=None, message_id=None,
                     GAME_ACTION=False, user=None):
    global PLAYERS
    PLAYERS = players
    global PLAYER_CHANNELS
    PLAYER_CHANNELS = player_channels
    global PLAYS
    PLAYS = plays
    global HANDS
    HANDS = hands
    global CLIENT
    CLIENT = client
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
    if GAME_ACTION:
        await game_action(CLIENT.get_guild(guild_id), 'Exploding Kittens', user)
    else:
        await GAME(payload, guild_id, channel, message_id)
    return (    players,
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
                future_message
            )


async def GAME(payload, guild_id, channel, message_id):
    print(str(payload.member).split('#')[0].lower() +
          str(payload.member).split('#')[1],
          str(channel.name))
    if str(channel.name) == str(payload.member).split('#')[0].lower() + str(payload.member).split('#')[1]:
        if str(payload.emoji) == '☑️':
            PLAYS[guild_id][payload.member].append(message_id)
            print(payload.member, PLAYS[guild_id][payload.member])
        if str(payload.emoji) == '🃏':
            print('got favor!')
            sender_channel = PLAYER_CHANNELS[guild_id][payload.member]
            sender_message = await sender_channel.fetch_message(message_id)
            card = str(sender_message.content)
            favor_channel = PLAYER_CHANNELS[guild_id][FAVOR_USER[guild_id]]
            card_message = await favor_channel.send(card)
            if 'card' not in card and card != 'defuse' and card != 'nope':
                await card_message.add_reaction('☑️')
            HANDS[guild_id][FAVOR_USER[guild_id]].append(card_message)
            HANDS[guild_id][payload.member].remove(sender_message)
            for card_message in HANDS[guild_id][payload.member]:
                await card_message.remove_reaction('🃏', CLIENT.user)
            await sender_message.delete()
            Favor[guild_id] = False
            temp_FAVOR_USER = FAVOR_USER[guild_id]
            FAVOR_USER[guild_id] = None
            FAVOR_TARGET[guild_id] = None
            FAVOR_TARGET_LIST[guild_id] = []
            STATE[guild_id][0] = 'playing'
            await game_action(CLIENT.get_guild(guild_id), 'Exploding Kittens', temp_FAVOR_USER)
    else:
        await MAIN_CHANNEL[guild_id].send('server owner is now cheating')
    await game_action(CLIENT.get_guild(guild_id), STATE[guild_id][1], payload.member)

    return


async def game_action(guild, game, player):
    print(guild, player, game)
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
                await action_container.delete()
            print(PLAYER_TURN[guild.id][0],
                  NEXT_TURN[guild.id], DOUBLE_TURN[guild.id])
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
                message = await PLAYER_CHANNELS[guild.id][PLAYER_TURN[guild.id][0]].send('draw')
                await message.add_reaction('☑️')
                TURN_MESSAGE[guild.id] = message
            print(PLAYER_TURN[guild.id][0],
                  NEXT_TURN[guild.id], DOUBLE_TURN[guild.id])
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
            if 'defuse' not in HANDS[guild.id][player]:
                await MAIN_CHANNEL[guild.id].send(player.mention + ' doesn\'t has a defuse\n' + '😵')
                PLAYER_TURN[guild.id].remove(player)
            else:
                await MAIN_CHANNEL[guild.id].send(player.mention + ' has a defuse\n' + 'please enter number between -1 and 99 to put a bomb back to DECK (0 = top of DECK, -1 = bottom of DECK)')
                DEFUSE[guild.id][player].pop()
                for card in HANDS[guild.id][player]:
                    if str(card.content) == 'defuse':
                        HANDS[guild.id][player].remove(card)
                        break
        else:
            card_message = await channel.send(card)
            if 'card' not in card and card != 'defuse' and card != 'nope':
                await card_message.add_reaction('☑️')
            HANDS[guild.id][player].append(card_message)
        NEXT_TURN[guild.id] = True


async def SEE_THE_FUTURE(guild, game, player, channel):
    global FUTURE_MESSAGE
    if game == 'Exploding Kittens':
        action_message = await MAIN_CHANNEL[guild.id].send('see the future' + '!')
        await action_message.add_reaction('🚫')
        message = '```'
        for i in range(3):
            message += '\n' + str(i+1) + ' : ' + DECK[guild.id][i]
        message += '```'
        FUTURE_MESSAGE[guild.id] = await channel.send(message)


async def SHUFFLE(guild, game, player, channel):
    if game == 'Exploding Kittens':
        action_message = await MAIN_CHANNEL[guild.id].send('shuffle' + '!')
        await action_message.add_reaction('🚫')
        random.shuffle(DECK[guild.id])
        return


async def FAVOR(guild, game, player, channel):
    global Favor
    if game == 'Exploding Kittens':
        action_message = await MAIN_CHANNEL[guild.id].send('favor' + '!')
        await action_message.add_reaction('🚫')
        Favor[guild.id] = True
        FAVOR_USER[guild.id] = player
        STATE[guild.id][0] = 'select favor target'
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
    if game == 'Exploding Kittens':
        action_message = await MAIN_CHANNEL[guild.id].send('skip' + '!')
        await action_message.add_reaction('🚫')
        NEXT_TURN[guild.id] = True
        await TURN_MESSAGE[guild.id].delete()


async def ATTACK(guild, game, player, channel):
    global NEXT_TURN
    global DOUBLE_TURN
    if game == 'Exploding Kittens':
        action_message = await MAIN_CHANNEL[guild.id].send('attack ' + PLAYER_TURN[guild.id][1].mention + '!')
        await action_message.add_reaction('🚫')
        DOUBLE_TURN[guild.id] += 1
        NEXT_TURN[guild.id] = True
        await TURN_MESSAGE[guild.id].delete()


async def PAIR(guild, game, player, channel):
    if game == 'Exploding Kittens':
        return


async def THREE_OF_A_KIND(guild, game, player, channel):
    if game == 'Exploding Kittens':
        return


async def FIVE_UNIQUE(guild, game, player, channel):
    if game == 'Exploding Kittens':
        return
