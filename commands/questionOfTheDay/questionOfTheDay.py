import discord
from discord.ext import commands, tasks
import random
import json
import inflect # this takes in numbers and turns them into words. used for converting an interator into an emoji choice
import emoji
import time
import re
from datetime import datetime

'''
I'm putting this command on haitus
until discord.py supports buttons

But that won't be for a long time
'''


'''
NOTES

The questions should be posted to the same channel every single day
each question should have some canned options. Should aim for 3

They should all be in a embed so I can put in images and such

Should have the option to privately vote. 

should store options in a MYSQL database

There sould be a cache of question numbers.
if the question was asked in the last X days, 
it should be skipped and pick a new one, check again etc...

Eventually there should be a roundup of the responses,
once a week? once a month?
'''

async def getQuestion(ctx=None, client=None, randomQuestion=None, questionBoard=None, serverSettings=None, server=None):
    '''
    I'm too tired to implement this
    but due to the way I am doing tasks, I cannot use ctx

    thus, I have to read the server ID from the server settings json file
    
    '''


    # this is the new cache system
    with open('./commands/questionOfTheDay/questionCache.json', encoding='utf-8') as file:
        cache = json.load(file)
    cacheWhole  = cache
    try:    # cache exists
        cache   = cache[str(server)]
        cacheExists = True
        print(datetime.now().strftime("%Y-%m-%d %I:%M:%S:%f %p") + ' Cache Exists')
    except: # cache doesnt exist
        #cacheWhole = {str(server): []}
        cache[str(server)] = [] 
        cacheExists = False
        print(datetime.now().strftime("%Y-%m-%d %I:%M:%S:%f %p") + ' Cache does not exist')

    # doing the actual sorting
    try:    # if fails, it should mean that they dont have a cache
        cache = sorted(cache, key= lambda i: i["asked"])    # sorting from oldest [0] to youngest [list.size]    
    except:
        print(datetime.now().strftime("%Y-%m-%d %I:%M:%S:%f %p") + ' QOTD ' + str(server) + ': Cache failed sorting...')

    # loading all questions
    with open('./commands/questionOfTheDay/questionOfTheDay_QuestionList.json', encoding='utf-8') as file:
        quesions = json.load(file)

    '''
    if isinstance(questionBoard, int):
        questionBoard = client.get_channel(questionBoard)
    '''

    #print(datetime.now().strftime("%Y-%m-%d %I:%M:%S:%f %p") + ' ' + str(quesions[]))
    
    questionBoard = client.get_channel(int(serverSettings[server]['questionOfTheDay']['channelID']))

    if randomQuestion == None:      # if there was a manually specified question
        while True:                 # just do it
            questionNumber = random.randint(0,(len(quesions['questions']) - 1)) # get a random question id

            '''
            the idea is that, it defaults to thinking the pulled question
            is not in the cache (as in the boolean isQuestionInCache=False).
            so it goes through each entry in the cache
            if the pulled question ID matches a question in the cache
            it sets this boolean to True

            Then there is a if else check
            if it is true, it reruns the while loops with "continue"
            thus pulls a new question

            if the boolean is false
            it pops the first element in the sorted cache (b/c it is sorted oldest to youngest)
            then appends a new entry to the end of the cache list

            then it will write to file
            '''

            '''
            There is a bug where cache is saving as

            "serverID": {
                "question": xxxx,
                "asked": xxxxxxxxxx
            }

            instead of

            "serverID": [
                {
                    "question": xxxx,
                    "asked": xxxxxxxxxx
                }
            ]
            '''


            if cacheExists:
                isQuestionInCache = False
                for question in cache:
                    print(datetime.now().strftime("%Y-%m-%d %I:%M:%S:%f %p") + ' pulled question number = ' + str(questionNumber))
                    print(datetime.now().strftime("%Y-%m-%d %I:%M:%S:%f %p") + ' question in cache = ' + str(question))
                    if int(questionNumber) == int(question['question']):
                        isQuestionInCache = True

                if isQuestionInCache:
                    # the question has been asked recently
                    # pull another question
                    continue
                else:
                    # this is a new question

                    # is there room in the cache?
                    if len(cache) >= serverSettings[server]['questionOfTheDay']['cacheSize']:
                        cache.pop(0)    # remove the oldest question

                    cache.append({'question': questionNumber, "asked": int(time.time())})

                    # testing this
                    #cache = {str(ctx.guild.id): cache}  # this appears to only work for one server
                    cacheWhole[str(server)] = cache # this should work with multiple servers, needs testing

                    with open('./commands/questionOfTheDay/questionCache.json', 'w') as file:
                        json.dump(cacheWhole, file, indent=4)
                    break
            else:
                #cache[0] = ({'question': questionNumber, "asked": int(time.time())})

                # testing this
                #cache = {str(ctx.guild.id): cache}  # this appears to only work for one server
                cacheWhole[str(server)] = ([{'question': questionNumber, "asked": int(time.time())}]) # this should work with multiple servers, needs testing

                with open('./commands/questionOfTheDay/questionCache.json', 'w') as file:
                    json.dump(cacheWhole, file, indent=4)
                break

        randomQuestion = quesions['questions'][questionNumber]  # getting the random question
    else:
        randomQuestion = quesions['questions'][randomQuestion]

    description = ''
    
    # trying to see if the question has a URL property
    try: 
        questionURL = randomQuestion['url']
    except:
        questionURL = None
    
    p = inflect.engine()

    try:
        for key in randomQuestion['answers'].keys():
            description += ':' + p.number_to_words(key) + ': ' + randomQuestion['answers'][key] + '\n'
    except:
        description = "Go and tell the server in <#791375988008288266>"

    #print(description)

    embed = discord.Embed(
        title = randomQuestion['question'],
        description = description,
        url = questionURL
    )
    embed.set_footer(text="Question ID: " + str(randomQuestion['id']) + ' of ' + str(len(quesions['questions'])))

    await questionBoard.send('<@&790300861666295860> give me your opinions',embed=embed)

    #questionMessage = await ctx.fetch_message(questionBoard.last_message_id)
    questionMessage = await questionBoard.history(limit=1).flatten()
    questionMessage = questionMessage[0]
    
    try:
        for key in randomQuestion['answers'].keys():
            emojis = discord.utils.get(questionBoard.guild.emojis, name=str)

            # im fucking tired, i hate how unicode works
            if int(key) == 0:
                await questionMessage.add_reaction('\N{DIGIT ZERO}\N{COMBINING ENCLOSING KEYCAP}')
            elif int(key) == 1:
                await questionMessage.add_reaction('\N{DIGIT ONE}\N{COMBINING ENCLOSING KEYCAP}')
            elif int(key) == 2:
                await questionMessage.add_reaction('\N{DIGIT TWO}\N{COMBINING ENCLOSING KEYCAP}')
            elif int(key) == 3:
                await questionMessage.add_reaction('\N{DIGIT THREE}\N{COMBINING ENCLOSING KEYCAP}')
            elif int(key) == 4:
                await questionMessage.add_reaction('\N{DIGIT FOUR}\N{COMBINING ENCLOSING KEYCAP}')
            elif int(key) == 5:
                await questionMessage.add_reaction('\N{DIGIT FIVE}\N{COMBINING ENCLOSING KEYCAP}')
            elif int(key) == 6:
                await questionMessage.add_reaction('\N{DIGIT SIX}\N{COMBINING ENCLOSING KEYCAP}')
            elif int(key) == 7:
                await questionMessage.add_reaction('\N{DIGIT SEVEN}\N{COMBINING ENCLOSING KEYCAP}')
            elif int(key) == 8:
                await questionMessage.add_reaction('\N{DIGIT EIGHT}\N{COMBINING ENCLOSING KEYCAP}')
            elif int(key) == 9:
                await questionMessage.add_reaction('\N{DIGIT NINE}\N{COMBINING ENCLOSING KEYCAP}')
    except:
        print(datetime.now().strftime("%Y-%m-%d %I:%M:%S:%f %p") + ' QOTD ' + str(server) + ': Error in adding buttons from question ' + str(randomQuestion['id']))