import discord
from discord.ext import commands, tasks
import json
import random

async def addCringe(ctx=None, client=None, user=None, userDatabase=None):

    # read users database
    with open(userDatabase, encoding='utf-8') as file:
        users = json.load(file)

    try:
        userBonks = users[str(user.id)]['cringe']
    except:
        users[str(user.id)] = {"cringe": 0}
    users[str(user.id)]['cringe'] = (int(users[str(user.id)]['cringe']) + 1)

    with open(userDatabase, 'w') as file:
        json.dump(users, file, indent=4)

    
    randomMessage = [
        (user.mention + ' has been mega cringe ' + str(users[str(user.id)]['cringe']) + ' times!'),
        (user.mention + ' committed cringe ' + str(users[str(user.id)]['cringe']) + ' times!'),
        (user.mention + ' posted cringe ' + str(users[str(user.id)]['cringe']) + ' times!')
    ]
    

    await ctx.send(randomMessage[random.randint(0,len(randomMessage) - 1)])

async def getCringe(ctx=None, client=None, user=None, userDatabase=None):
     # read users database
    with open(userDatabase, encoding='utf-8') as file:
        users = json.load(file)

    try:
        userBonks = (users[str(user.id)]['cringe'])

        randomMessage = [
        (user.mention + ' has been mega cringe ' + str(users[str(user.id)]['cringe']) + ' times!'),
        (user.mention + ' committed cringe ' + str(users[str(user.id)]['cringe']) + ' times!'),
        (user.mention + ' posted cringe ' + str(users[str(user.id)]['cringe']) + ' times!')
    ]

        if (userBonks != 0) and (userBonks != None) and (userBonks > 0):
            await ctx.send(randomMessage[random.randint(0,len(randomMessage) - 1)])
        else:
            await ctx.send(user.mention + ' is based and has never been cringe!')
    except KeyError:
        await ctx.send(user.mention + ' is based and has never been cringe!')
    