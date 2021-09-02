import discord
from discord.ext import commands, tasks
import json
import random

async def addSmart(ctx=None, client=None, user=None, userDatabase=None):

    # read users database
    with open(userDatabase, encoding='utf-8') as file:
        users = json.load(file)

    try:
        userBonks = users[str(user.id)]['smart']
    except:
        users[str(user.id)]['smart'] = 0
    users[str(user.id)]['smart'] = (int(users[str(user.id)]['smart']) + 1)

    with open(userDatabase, 'w') as file:
        json.dump(users, file, indent=4)

    
    randomMessage = [
        (user.mention + ' has expanded their brain ' + str(users[str(user.id)]['smart']) + ' times!'),
        (user.mention + ' has been on the deans list ' + str(users[str(user.id)]['smart']) + ' times!'),
        (user.mention + ' has ' + str(users[str(user.id)]['smart']) + ' wrinkles on their brain!')
    ]
    

    await ctx.send(randomMessage[random.randint(0,len(randomMessage) - 1)])

async def getSmart(ctx=None, client=None, user=None, userDatabase=None):
     # read users database
    with open(userDatabase, encoding='utf-8') as file:
        users = json.load(file)

    try:
        userBonks = (users[str(user.id)]['smart'])

        randomMessage = [
        (user.mention + ' has expanded their brain ' + str(users[str(user.id)]['smart']) + ' times!'),
        (user.mention + ' has been on the deans list ' + str(users[str(user.id)]['smart']) + ' times!'),
        (user.mention + ' has ' + str(users[str(user.id)]['smart']) + ' wrinkles on their brain!')
        ]

        if (userBonks != 0) and (userBonks != None) and (userBonks > 0):
            await ctx.send(randomMessage[random.randint(0,len(randomMessage) - 1)])
        else:
            await ctx.send(user.mention + ' is dum and has never been smart!')
    except KeyError:
        await ctx.send(user.mention + ' is dum and has never been smart!')
    