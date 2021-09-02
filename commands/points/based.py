import discord
from discord.ext import commands, tasks
import json
import random

async def addBased(ctx=None, client=None, user=None, userDatabase=None):

    # read users database
    with open(userDatabase, encoding='utf-8') as file:
        users = json.load(file)

    try:
        userBonks = users[str(user.id)]['based']
    except:
        users[str(user.id)]['based'] = 0
    users[str(user.id)]['based'] = (int(users[str(user.id)]['based']) + 1)

    with open(userDatabase, 'w') as file:
        json.dump(users, file, indent=4)

    
    randomMessage = [
        (user.mention + ' has been mega based ' + str(users[str(user.id)]['based']) + ' times!'),
    ]
    

    await ctx.send(randomMessage[random.randint(0,len(randomMessage) - 1)])

async def getBased(ctx=None, client=None, user=None, userDatabase=None):
     # read users database
    with open(userDatabase, encoding='utf-8') as file:
        users = json.load(file)

    try:
        userBonks = (users[str(user.id)]['based'])

        randomMessage = [
            (user.mention + ' has been mega based ' + str(users[str(user.id)]['based']) + ' times!'),
        ]

        if (userBonks != 0) and (userBonks != None) and (userBonks > 0):
            await ctx.send(randomMessage[random.randint(0,len(randomMessage) - 1)])
        else:
            await ctx.send(user.mention + ' is cringe and has never been based!')
    except KeyError:
        await ctx.send(user.mention + ' is cringe and has never been based!')
    