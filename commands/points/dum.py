import discord
from discord.ext import commands, tasks
import json
import random

async def addDum(ctx=None, client=None, user=None, userDatabase=None):

    # read users database
    with open(userDatabase, encoding='utf-8') as file:
        users = json.load(file)

    try:
        userBonks = users[str(user.id)]['dum']
    except:
        users[str(user.id)]['dum'] = 0
    users[str(user.id)]['dum'] = (int(users[str(user.id)]['dum']) + 1)

    with open(userDatabase, 'w') as file:
        json.dump(users, file, indent=4)

    
    randomMessage = [
        (user.mention + ' has been mega dum ' + str(users[str(user.id)]['dum']) + ' times!'),
        (user.mention + ' drooled all over ' + str(users[str(user.id)]['dum']) + ' times!'),
        (user.mention + ' flunked ' + str(users[str(user.id)]['dum']) + ' semesters!')
    ]
    

    await ctx.send(randomMessage[random.randint(0,len(randomMessage) - 1)])

async def getDum(ctx=None, client=None, user=None, userDatabase=None):
     # read users database
    with open(userDatabase, encoding='utf-8') as file:
        users = json.load(file)

    try:
        userBonks = (users[str(user.id)]['dum'])

        randomMessage = [
        (user.mention + ' has been mega dum ' + str(users[str(user.id)]['dum']) + ' times!'),
        (user.mention + ' drooled all over ' + str(users[str(user.id)]['dum']) + ' times!'),
        (user.mention + ' flunked ' + str(users[str(user.id)]['dum']) + ' semesters!')
        ]

        if (userBonks != 0) and (userBonks != None) and (userBonks > 0):
            await ctx.send(randomMessage[random.randint(0,len(randomMessage) - 1)])
        else:
            await ctx.send(user.mention + ' is smort and has never been dum!')
    except KeyError:
        await ctx.send(user.mention + ' is smort and has never been dum!')
    