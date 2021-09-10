import discord
from discord.ext import commands, tasks
import json
import random

async def addBonk(ctx=None, client=None, user=None, userDatabase=None):

    # read users database
    with open(userDatabase, encoding='utf-8') as file:
        users = json.load(file)

    try:
        userBonks = users[str(user.id)]['bonk']
    except:
        users[str(user.id)] = {"bonk": 0}
    users[str(user.id)]['bonk'] = (int(users[str(user.id)]['bonk']) + 1)

    with open(userDatabase, 'w') as file:
        json.dump(users, file, indent=4)

    randomMessage = [
        (user.mention + ' has committed a horny ' + str(users[str(user.id)]['bonk']) + ' times! <a:doggoHammer:883162592795828244>'),
        (user.mention + ' has been horny ' + str(users[str(user.id)]['bonk']) + ' times! <a:doggoHammer:883162592795828244>'),
        (user.mention + ' has been bonked by the horny hammer ' + str(users[str(user.id)]['bonk']) + ' times! <a:doggoHammer:883162592795828244>'),
        (user.mention + ' has been very naughty ' + str(users[str(user.id)]['bonk']) + ' times! <a:doggoHammer:883162592795828244>')
    ]

    await ctx.send(randomMessage[random.randint(0,3)])

async def getBonks(ctx=None, client=None, user=None, userDatabase=None):
     # read users database
    with open(userDatabase, encoding='utf-8') as file:
        users = json.load(file)

    try:
        userBonks = (users[str(user.id)]['bonk'])
        print(userBonks)
        if (userBonks != 0) and (userBonks != None) and (userBonks > 0):
            randomMessage = [
                (user.mention + ' has commited a horny ' + str(userBonks) + ' times! <a:doggoHammer:883162592795828244>'),
                (user.mention + ' has been horny ' + str(userBonks) + ' times! <a:doggoHammer:883162592795828244>'),
                (user.mention + ' has been bonked by the horny hammer ' + str(userBonks) + ' times! <a:doggoHammer:883162592795828244>'),
                (user.mention + ' has been very naughty ' + str(userBonks) + ' times! <a:doggoHammer:883162592795828244>')
            ]

            await ctx.send(randomMessage[random.randint(0,3)])
        else:
            await ctx.send(user.mention + ' is pure and has yet to succumb to their lust!')
    except KeyError:
        await ctx.send(user.mention + ' is pure and has yet to succumb to their lust!')
    