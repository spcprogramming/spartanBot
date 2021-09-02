# Work with Python 3.6
import discord
from discord.ext import commands, tasks
import json, operator
import os
import requests
from datetime import datetime
import logging, sys
import re
from urllib.parse import urlparse
import urllib
import asyncio
import time

# custom functions
from commands.questionOfTheDay import questionOfTheDay
#from commands.politicalTest import politicalTest
from commands.points import bonk
from commands.points import based
from commands.points import cringe
from commands.points import dum
from commands.points import smart

# read secrets
with open('secrets.txt') as f:
    TOKEN = str(f.readline())

client = discord.Client()
client = commands.Bot(command_prefix = '!!')

cacheFileName = 'cache'

ignoreChannels = [729885603591618601,	# roles channel
				  409910783158255616,	# announcement channel
				  624759106930081812,	# notification channel
				  450381990470877186,	# bot spam channel
				  747930008835588156,	# helping bot 3
				  803789404723871805]	# qotd question channel

pictureFileFormats = ['jpg', 'png', 'gif', 'jpeg', 'tiff', 'bmp']

# loading server settings
with open('./commands/serverInfo/serverDatabase.json', encoding='utf-8') as file:
	serverSettings = json.load(file)

DEBUG = False

def debugLog(s):
	if DEBUG:
		print(s)

def getInfoMessage(reaction):
	return reaction.message

def getInfoEmoji(reaction):
	return reaction.emoji

def inCache(id):
	with open(cacheFileName, 'r') as cache:
		for line in cache:
			if str(id) in line:
				return int(next(cache))
	cache.close()
	return False

def writeToCache(message, starBoard):
	with open(cacheFileName, 'a') as cache:
		cache.write(str(message.id) + '\n')
		cache.write(str(starBoard.last_message_id) + '\n')
	cache.close()

def isEmojiAvailable(id):
	for emoji in client.emojis:
		if id == emoji.id:
			return True
	return False

def urlValid(url):
	req = Request(url)
	try:
		response = urlopen(req)
	except(URLError, e):
		if hasattr(e, 'reason'):
			return False
		elif hasattr(e, 'code'):
			return False
	else:
		return True

@client.event
async def on_ready():
	await client.change_presence(status=discord.Status.online, activity=discord.Game("!!h for help"))
	print(datetime.now().strftime("%Y-%m-%d %I:%M:%S:%f %p") + ' \nRinBot is ONLINE, listening for actions...\n')

@tasks.loop(seconds=30)
async def checkTime():

	'''
	Im too tired to implement this,
	but because of the way I'm doing looped tasks I cannot use ctx

	so this task should loop every 30 seconds
	it should read the server settings, interating over every server entry
	it should then read the time they want their questions
	if that time is right now, it should run the qotd functions

	then interating for the next server
	'''

	timeformat = '%H:%M'
	timeNow = datetime.strftime(datetime.now(), timeformat)

	# read server settings to see if they want questions
	for server in serverSettings:	# server in specific interation is serverSettings[server]
		print('Server: ' + str(server))
		#print('Server Settings: ' + str(serverSettings[server]))

		if serverSettings[server]['questionOfTheDay']['enabled']:
			# QOTD IS ENABLED
			print(datetime.now().strftime("%Y-%m-%d %I:%M:%S:%f %p") + ' QOTD ' + str(server) + ': ENABLED')
			timeQOTD = serverSettings[server]['questionOfTheDay']['time']
			channelQOTD = client.get_channel(serverSettings[server]['questionOfTheDay']['channelID'])

			print(datetime.now().strftime("%Y-%m-%d %I:%M:%S:%f %p") + ' Time now: ' +  str(timeNow))
			print(datetime.now().strftime("%Y-%m-%d %I:%M:%S:%f %p") + ' QOTD time: ' + str(timeQOTD))
			print('-------------------------------------------------------------------------------------------')

			if (str(timeNow) == str(timeQOTD)):
				print(datetime.now().strftime("%Y-%m-%d %I:%M:%S:%f %p") + ' Attempting to post QOTD to ' + str(server))
				await questionOfTheDay.getQuestion(ctx=None, client=client, randomQuestion=None, serverSettings=serverSettings, server=server)
				await asyncio.sleep(60)
		else:
			# QOTD NOT ENABLED
			print(datetime.now().strftime("%Y-%m-%d %I:%M:%S:%f %p") + ' QOTD ' + str(server) + ': DISABLED')
			print('-------------------------------------------------------------------------------------------')
'''
	if (str(timeNow) == str(timeQOTD)):
		print(datetime.now().strftime("%Y-%m-%d %I:%M:%S:%f %p") + ' Posting QOTD')
		await questionOfTheDay.getQuestion(ctx=None, client=client, randomQuestion=None)
		await asyncio.sleep(60)
		'''

@checkTime.before_loop
async def before():
	await client.wait_until_ready()
	print(datetime.now().strftime("%Y-%m-%d %I:%M:%S:%f %p") + ' Time has finished waiting')

@client.event
async def on_reaction_add(reaction, user):

	# get info
	message = getInfoMessage(reaction)
	emoji = getInfoEmoji(reaction)
	serverID = message.guild.id

	# variables that wont work globally cause im dumb and lazy

	with open('./commands/serverInfo/serverDatabase.json', encoding='utf-8') as file:
		serverSettings = json.load(file)
	
	starBoard = client.get_channel(serverSettings[str(serverID)]['starBoard']['channelID'])
	minReact = serverSettings[str(serverID)]['starBoard']['minimumReact']
	#leaderBoard = client.get_channel(starBoardLeaderBoardID)
	containsVideo = False

	# does the reaction count of this emoji outnumber the min reaction set?
	# does this reaction take place in an allowed channel?
	# is the emoji even available?
	# and in cache ( this is a new message )
	if ((reaction.count >= minReact) and
		(message.channel.id not in ignoreChannels) and
		((reaction.custom_emoji == False) or (isEmojiAvailable(emoji.id))) and
		(inCache(message.id) != False)):
		debugLog('Found in cache...')
		debugLog((str(emoji.name) if reaction.custom_emoji else str(emoji)) + ' added to message ' + str(message.id) + ', total ' + (str(emoji.name) if reaction.custom_emoji else str(emoji)) + ': ' + str(reaction.count))
		messageToUpdate = await starBoard.fetch_message(inCache(message.id))
		content = []
		for item in message.reactions:
			if (item.count >= minReact) and ((item.custom_emoji == False) or isEmojiAvailable(item.emoji.id)):
				content.append(str(item.emoji) + ' **' + str(item.count) + '** ')
		convertList = [str(element) for element in content]		# convert the list
		await messageToUpdate.edit(content=(' ,  '.join(convertList)))	# edit the bot message to the correct list and number of emojis

	elif ((reaction.count >= minReact) and
		(message.channel.id not in ignoreChannels) and
		((reaction.custom_emoji == False) or isEmojiAvailable(emoji.id)) and
		(inCache(message.id) == False)):	# if this is a new star message
		debugLog((str(emoji.name) if reaction.custom_emoji else str(emoji)) + ' added to message ' + str(message.id) + ', total ' + (str(emoji.name) if reaction.custom_emoji else str(emoji)) + ': ' + str(reaction.count))

		starEmbed = discord.Embed(
			title = str(message.author),
			description = str(message.content),
		)
		starEmbed.set_footer(text='ID: ' + str(message.id) + ' - ' + str(message.created_at.strftime('%m/%d/%Y, %I:%M:%S %p EST')))
		starEmbed.set_author(name=str(message.author), icon_url=str(message.author.avatar_url))
		starEmbed.add_field(name='Source', value="[Jump!](" + message.jump_url + ")", inline=False)

		# checking media
		try: 	# trying to look for linked media
			if urlValid(re.search("(?P<url>https?://[^\s]+)", message.content).group("url")):	# is a url
				if any(x in re.search("(?P<url>https?://[^\s]+)", message.content).group("url") for x in pictureFileFormats):	# if it has a picture linked
					starEmbed.set_image(url=str(re.search("(?P<url>https?://[^\s]+)", message.content).group("url")))
					debugLog('Attached linked image... ' + re.search("(?P<url>https?://[^\s]+)", message.content).group("url"))
				else:	# something is linked but its not a picture, this will make it so that will upload the file
					r = requests.get(message.attachments[0].url, allow_redirects=True)
					open('temp', 'wb').write(r.content)
					containsVideo = True
			else:	# if there was an attached image
				if len(message.attachments) > 0:
					if any(x in message.attachments[0].url for x in pictureFileFormats):	# picture was attached
						starEmbed.set_image(url=str(message.attachments[0].url))
						debugLog('Attached sent image...')
					else:	# something else wat attached
						r = requests.get(message.attachments[0].url, allow_redirects=True)
						open('temp', 'wb').write(r.content)
						containsVideo = True
		except:		# if there was nothing linked and it made and exception
			if len(message.attachments) > 0:
				if any(x in message.attachments[0].url for x in pictureFileFormats):
					starEmbed.set_image(url=str(message.attachments[0].url))
					debugLog('Attached sent image...')
				else:
					r = requests.get(message.attachments[0].url, allow_redirects=True)
					open('temp', 'wb').write(r.content)
					containsVideo = True


		if containsVideo:
			await starBoard.send(str(reaction.emoji) + ' **' + str(reaction.count) + '** ',embed=starEmbed, file=(discord.File('temp')))
		else:
			await starBoard.send(str(reaction.emoji) + ' **' + str(reaction.count) + '** ',embed=starEmbed)

		# writing the message to cache
		writeToCache(message, client.get_channel(serverSettings[str(serverID)]['starBoard']['channelID']))

@client.command()
async def duolingo(ctx, user=None):
	if user==None:
		embed = discord.Embed(	# make embed
			title = 'Server Duolingo Leaderboard'
		)

		leaderboard = getDuolingoLeaderboard()	# gets info from my friends list

		for person in leaderboard:	# for each person in my friends list
			url = 'https://www.duolingo.com/2017-06-30/users/' + str(person['id']) + '?fields=courses'	# the url to get info on my friends and myself
			languageFlagString = ''	# empty string that i will populate with flag emojis
			with urllib.request.urlopen(url) as urltest:	# load courses that this person is taking
				data = json.loads(urltest.read().decode())	# load the json for this person

			for course in data['courses']:	# for each course this person is taking
				languageName = course['title']	# just get the title of the course
				languageFlagString += (languageFind(languageName) + ' ')	# get the flag and add it to the flag list string

			embed.add_field(name=(duolingoUserFind(str(person['username'])) + ' ' + languageFlagString), value=person['points'], inline=False)	# make embed
		await ctx.send(embed=embed)	# send embed
	else:
		if user=='join':
			await ctx.send('If you would like to join us in Duolingo, ping or dm <@183680648408465408> for assistance')
			return
		if(duolingoUserFind(ctx.message.mentions[0].id)) == False:

			await ctx.send("Looks like that user is not learning with the server.\nIf you are this person, ping or DM <@183680648408465408> to join!")
			return

		url = 'https://www.duolingo.com/2017-06-30/users/' + str(duolingoUserFind(ctx.message.mentions[0].id)) + '?fields=courses'	# the url to get info on my friends and myself
		embed = discord.Embed(	# make embed
			title = 'Duolingo stats for ' + str(ctx.message.mentions[0])
		)
		with urllib.request.urlopen(url) as urltest:	# load courses that this person is taking
			data = json.loads(urltest.read().decode())	# load the json for this person

		userPoints = ''	# empty string that i will populate with data
		userCrowns = ''# empty string that i will populate with data
		for course in data['courses']:	# for each course this person is taking
			languageName = course['title']	# just get the title of the course
			userPoints += (languageFind(languageName) + " **" + str(course['xp']) + '**\n')	# get the flag and add it to the flag list string
			userCrowns += ("**" + str(course['crowns']) + '**\n')

		embed.add_field(name=":united_nations: Points", value=(userPoints), inline=True)
		embed.add_field(name=":crown: Crowns", value=(userCrowns), inline=True)

			#embed.add_field(name=(languageFind(languageName) + '**' + str(course['xp']) + '**'), value='​', inline=True)
			#embed.add_field(name=':crown: ' + '**' + str(course['crowns']) + '**', value='​', inline=True)
			#embed.add_field(name='​', value='​', inline=False)
		await ctx.send(embed=embed)

@client.command()
async def userInfo(ctx, mention=None):
	if mention == None:
		await ctx.send('Hey dummy, you didn\'t tell me who you wanted info on... \nEither @ them or give me their user ID.')
		return

	if len(ctx.message.mentions) == 0:
		try:
			mention = await client.fetch_user(int(mention))
		except:
			await ctx.send('I could not find who you were talking about with that user ID. \nPlease try again...')
			return
	else:
		try:
			mention = ctx.message.mentions[0]
		except:
			await ctx.send('I do not know how, but I failed to get the user from your mention.\nCould you try that again with their user ID?')
			return

	embed = discord.Embed(
		title = str(mention) + ' info...',
		color = 9834751
	)
	embed.add_field(name="Name:", value=str(mention), inline=False)

	embed.add_field(name="Nickname:", value=str(mention.display_name), inline=False)

	embed.add_field(name="ID:", value=str(mention.id), inline=False)

	embed.add_field(name="Is Bot:", value=str(mention.bot), inline=False)

	embed.add_field(name="Profile Picture URL:", value=str(mention.avatar_url), inline=False)
	embed.set_thumbnail(url=mention.avatar_url)

	embed.add_field(name="Animated Profile Picture:", value=str(mention.is_avatar_animated()), inline=False)

	embed.add_field(name="Created Account:", value=mention.created_at.strftime('%m/%d/%Y, %I:%M:%S %p EST'), inline=False)

	await ctx.send(embed=embed)

@client.command()
async def emojis(ctx):
	embeds = list()

	for server in client.guilds:	# for each server it is connected # TODO:
		embed = discord.Embed()
		emojisString = ''
		animatedString = ''

		for emoji in server.emojis:

			if emoji.animated == False:
				if emojisString == '':
					emojisString += str(emoji)
				else:
					emojisString += ' ' + str(emoji)
			else:
				if animatedString == '':
					animatedString += str(emoji)
				else:
					animatedString += ' ' + str(emoji)

		if emojisString != '':
			embed.add_field(name=str(server.name + ' Emojis'), value=emojisString, inline=False)
			print(datetime.now().strftime("%Y-%m-%d %I:%M:%S:%f %p") + ' emojiString: ' + str(emojisString) + '\n')

		if animatedString != '':
			embed.add_field(name=str(server.name + ' Animated Emojis'), value=animatedString, inline=False)
			print(datetime.now().strftime("%Y-%m-%d %I:%M:%S:%f %p") + ' animatedString: ' + str(animatedString) + '\n\n')

		await ctx.send(embed=embed)

@client.command()
async def starMin(ctx):
	with open('./commands/serverInfo/serverDatabase.json', encoding='utf-8') as file:
		serverSettings = json.load(file)
	await ctx.send("Minimum reactions to get on the star board is " + str(serverSettings[str(ctx.guild.id)]['starBoard']['minimumReact']) + " currently.")

@client.command()
async def tumblrBot(ctx):
	if ctx.author.id in [183680648408465408,420958938457047040,360571166416437250]:
		await tumblr.main(ctx)
		await ctx.send("Memes, stolen :sunglasses:")
	else:
		await ctx.send("You do not have the authority to run that command")

@client.command()
async def povertyReact(ctx, emojiName=None, messageID=None):
	if (emojiName == None) or (messageID == None):	# if they are dumb
		await ctx.send('Sorry, I could not understand your request. \nRemember, the usage of this command is \n`!!povertyReact EMOJI_NAME MESSAGE_LINK` and it *is* case sensitive')
		return

	# verifying that there is a message link or ID, then getting the ID from link and the message
	if (('http' not in messageID) and (int(messageID) < 0) ) or (len(messageID.split('/') ) != 7):	# if its not a link and its not a id
		await ctx.send('Sorry, I cannot find a message with the link or ID you provided')
		return
	elif ('http' in messageID):	# if its a link
		messageID = int(messageID.split('/')[6])

	try:	# try to get the message
		messageID = await ctx.fetch_message(messageID)
	except:	# cant get it
		await ctx.send('Sorry, I cannot find a message with the link you provided')

	# finding the emoji
	for emoji in ctx.guild.emojis:
		if (emoji.name == emojiName) and (emoji.animated == True):
			emojiName = emoji	# found emoji

	if isinstance(emojiName, str):	# could not fund emojie
		await ctx.send('Sorry, I could not find that animate emoji name. Did you spell it wrong? Is it even animated? This is case sensitive btw')
		return

	# add reaction
	await messageID.add_reaction(emojiName)

	# tell them
	await ctx.send(str(emojiName) + ' was added to the linked message')
'''
@client.command()
async def confession(ctx, *,message=None):
	await funcConfession.newConfession(ctx=ctx,confessionChannel = confessionChannel, client=client, message=message)
'''

'''
@client.command(name="forceQuestion")
async def forceQuestion(ctx, question=None, client=client, qotdChannel=None):
	
	print("hello")

	if question != None:
		print("question is not none")
		print(question)
		question = int(question)

	await questionOfTheDay.getQuestion(ctx=ctx, client=client, randomQuestion=question, questionBoard=qotdChannel, serverSettings=serverSettings[str(ctx.guild.id)])
'''

# Bonk Points
@client.command(name="bonk")
async def _bonk(ctx, user=None, client=client):

	# read user
	with open('./commands/usersInfo/userDatabase.json', encoding='utf-8') as file:
		users = json.load(file)
	
	# copying the mention system from userInfo
	if user == None:
		await ctx.send('Hey dummy! you didn\'t tell me who the horny is!')
		return
	
	try:
		user = ctx.message.mentions[0]
	except:
		print(datetime.now().strftime("%Y-%m-%d %I:%M:%S:%f %p") + " Failed obtaining user")
		return

	await bonk.addBonk(ctx=ctx, client=client, user=user, userDatabase=os.path.abspath('./commands/usersInfo/userDatabase.json'))

@client.command(name="bonks")
async def _bonks(ctx, user=None, client=client):
	if user == None:
		await ctx.send('Hey dummy! you didn\'t tell me who the horny is!')
		return
	
	try:
		user = ctx.message.mentions[0]
	except:
		print(datetime.now().strftime("%Y-%m-%d %I:%M:%S:%f %p") + " Failed obtaining user")
		return

	await bonk.getBonks(ctx=ctx, client=client, user=user, userDatabase=os.path.abspath('./commands/usersInfo/userDatabase.json'))

# Based Points
@client.command(name="based")
async def _based(ctx, user=None, client=client):

	# read user
	with open('./commands/usersInfo/userDatabase.json', encoding='utf-8') as file:
		users = json.load(file)
	
	# copying the mention system from userInfo
	if user == None:
		await ctx.send('Hey dummy! you didn\'t tell me who the based is!')
		return
	
	try:
		user = ctx.message.mentions[0]
	except:
		print(datetime.now().strftime("%Y-%m-%d %I:%M:%S:%f %p") + " Failed obtaining user")
		return

	await based.addBased(ctx=ctx, client=client, user=user, userDatabase=os.path.abspath('./commands/usersInfo/userDatabase.json'))

@client.command(aliases=['isBased', 'getBased'])
async def _isBased(ctx, user=None, client=client):
	if user == None:
		await ctx.send('Hey dummy! you didn\'t tell me who\' based!')
		return
	
	try:
		user = ctx.message.mentions[0]
	except:
		print(datetime.now().strftime("%Y-%m-%d %I:%M:%S:%f %p") + " Failed obtaining user")
		return

	await based.getBased(ctx=ctx, client=client, user=user, userDatabase=os.path.abspath('./commands/usersInfo/userDatabase.json'))

# Cringe Points 
@client.command(name="cringe")
async def _cringe(ctx, user=None, client=client):

	# read user
	with open('./commands/usersInfo/userDatabase.json', encoding='utf-8') as file:
		users = json.load(file)
	
	# copying the mention system from userInfo
	if user == None:
		await ctx.send('Hey dummy! you didn\'t tell me who\'s cringe is!')
		return
	
	try:
		user = ctx.message.mentions[0]
	except:
		print(datetime.now().strftime("%Y-%m-%d %I:%M:%S:%f %p") + " Failed obtaining user")
		return

	await cringe.addCringe(ctx=ctx, client=client, user=user, userDatabase=os.path.abspath('./commands/usersInfo/userDatabase.json'))

@client.command(aliases=['isCringe', 'getCringe'])
async def _isCringe(ctx, user=None, client=client):
	if user == None:
		await ctx.send('Hey dummy! you didn\'t tell me who\'s cringe!')
		return
	
	try:
		user = ctx.message.mentions[0]
	except:
		print(datetime.now().strftime("%Y-%m-%d %I:%M:%S:%f %p") + " Failed obtaining user")
		return

	await cringe.getCringe(ctx=ctx, client=client, user=user, userDatabase=os.path.abspath('./commands/usersInfo/userDatabase.json'))

# Dum Points 
@client.command(aliases=['dum', 'dumb'])
async def _Dum(ctx, user=None, client=client):

	# read user
	with open('./commands/usersInfo/userDatabase.json', encoding='utf-8') as file:
		users = json.load(file)
	
	# copying the mention system from userInfo
	if user == None:
		await ctx.send('Hey dummy! you didn\'t tell me who\'s dum!')
		return
	
	try:
		user = ctx.message.mentions[0]
	except:
		print(datetime.now().strftime("%Y-%m-%d %I:%M:%S:%f %p") + " Failed obtaining user")
		return

	await dum.addDum(ctx=ctx, client=client, user=user, userDatabase=os.path.abspath('./commands/usersInfo/userDatabase.json'))

@client.command(aliases=['isDum', 'getDum', 'isDumb', 'getDumb'])
async def _isDum(ctx, user=None, client=client):
	if user == None:
		await ctx.send('Hey dummy! you didn\'t tell me who\'s cringe!')
		return
	
	try:
		user = ctx.message.mentions[0]
	except:
		print(datetime.now().strftime("%Y-%m-%d %I:%M:%S:%f %p") + " Failed obtaining user")
		return

	await dum.getDum(ctx=ctx, client=client, user=user, userDatabase=os.path.abspath('./commands/usersInfo/userDatabase.json'))

# Smart Points
@client.command(aliases=['smart', 'smort'])
async def _smart(ctx, user=None, client=client):

	# read user
	with open('./commands/usersInfo/userDatabase.json', encoding='utf-8') as file:
		users = json.load(file)
	
	# copying the mention system from userInfo
	if user == None:
		await ctx.send('Hey dummy! you didn\'t tell me who\'s smart!')
		return
	
	try:
		user = ctx.message.mentions[0]
	except:
		print(datetime.now().strftime("%Y-%m-%d %I:%M:%S:%f %p") + " Failed obtaining user")
		return

	await smart.addSmart(ctx=ctx, client=client, user=user, userDatabase=os.path.abspath('./commands/usersInfo/userDatabase.json'))

@client.command(aliases=['isSmart', 'getSmart', 'isSmort', 'getSmort'])
async def _isSmart(ctx, user=None, client=client):
	if user == None:
		await ctx.send('Hey dummy! you didn\'t tell me who\'s smart!')
		return
	
	try:
		user = ctx.message.mentions[0]
	except:
		print(datetime.now().strftime("%Y-%m-%d %I:%M:%S:%f %p") + " Failed obtaining user")
		return

	await smart.getSmart(ctx=ctx, client=client, user=user, userDatabase=os.path.abspath('./commands/usersInfo/userDatabase.json'))

@client.command()
async def h(ctx):
	embed = discord.Embed(
		title = "Help",
		description = "RinBot is a star board bot made for the server.\nPosts that are good tend to get reactions from other users.",
		color = 9834751,
	)

	embed.add_field(name='starMin', value='Tells you the minimum reactions needed to get on the star board', inline=False)

	await ctx.send(embed=embed)

'''
STARTING TIME WATCH
'''
checkTime.start()

client.run(TOKEN)