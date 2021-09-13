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
import pickle

# custom functions
from commands.questionOfTheDay import questionOfTheDay
#from commands.politicalTest import politicalTest
from commands.points import bonk
from commands.points import based
from commands.points import cringe
from commands.points import dum
from commands.points import smart

from commands.SPCEvents import scan

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
				  803789404723871805,	# qotd question channel
				  882728909991460884,	# announcments
				  883093396892295238,   # server events
				  882732242202411059,	#roles
				  882759177620033566	# qotd
				  ]	
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
	reading spc events
	'''

	'''
	scanning for new ones
	'''
	scanTime = '14:16'
	timeformat = '%H:%M'
	timeNow = datetime.strftime(datetime.now(), timeformat)

	if (str(timeNow) == str(scanTime)):
		print(datetime.now().strftime("%Y-%m-%d %I:%M:%S:%f %p") + ' -> Scanning for SPC Events...')
		scan.main()




	# load the pickle

	#try:
	print('trying to load the cal pickle')
	pickle_in = open('./commands/SPCEvents/dict.pickle', 'rb')
	cal = pickle.load(pickle_in)
	total_events = cal
	print('pickle loaded')
	#print(cal)
	interation = 0
	for event in cal:
		'''
		get relative days
		then if it is 3 or less days
		post it
		move to next object

		exit loopcd
		remove from pickle list
		save pickle list
		'''
		#print('event: ' + str(event))
		#print('event datetime: ' + str(event['dateTime']))
		#diff = datetime.now() - event['dateTime']
		diff = event['dateTime'] - datetime.now()
		#print('day diff = ' + str(diff.days))
		total_events = cal
		notice_in_days = 2
		if ((int(diff.days) >= 0) and (int(diff.days) <= notice_in_days)):		# event in time windows
			print(datetime.now().strftime("%Y-%m-%d %I:%M:%S:%f %p") + ' -> ' + event['title'] + ' is happening in ' + str(diff.days) + ' days')
			await scan.postEvent(eventInfo=event, client=client)
			cal.pop(interation)
		else:
			if (int(diff.days) < 0):							# event passed
				#print(datetime.now().strftime("%Y-%m-%d %I:%M:%S:%f %p") + ' -> ' + event['title'] + ' has already passed (' + str(diff.days) + ' days)... Removing from cal')
				cal.pop(interation)
			elif (int(diff.days) > notice_in_days):							# in the future
				pass
				#print(datetime.now().strftime("%Y-%m-%d %I:%M:%S:%f %p") + ' -> ' + event['title'] + ' event too far into the future... (' + str(diff.days) + ' days)')
		#print('diffDays = ' + str(diff.days))
		interation += 1
	cal = total_events
	pickle_out = open('./commands/SPCEvents/dict.pickle', 'wb')
	pickle.dump(cal, pickle_out)
	pickle_out.close()

	#except Exception as e:
	#	print(datetime.now().strftime("%Y-%m-%d %I:%M:%S:%f %p") + ' Calender pickle could not be read.')
	#	print(e)
	#	pass
	

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
async def starMin(ctx):
	with open('./commands/serverInfo/serverDatabase.json', encoding='utf-8') as file:
		serverSettings = json.load(file)
	await ctx.send("Minimum reactions to get on the star board is " + str(serverSettings[str(ctx.guild.id)]['starBoard']['minimumReact']) + " currently.")

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