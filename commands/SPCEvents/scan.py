from discord import embeds
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
#from selenium.webdriver.firefox.options import Options
from titlecase import titlecase
import time
from datetime import datetime
import pickle
# Work with Python 3.6
import discord
from discord.ext import commands, tasks
import re
import asyncio
'''

event elements
    title
    date
    time

    campus
        address
    zoomlink

    description

'''
#cacheName = 'cache.txt'

#laoding cache
#with open(cacheName) as cache:
#    existing = [line.rstrip() for line in cache]

async def postEvent(eventInfo, ctx=None, client=None):

    # loading client stuff
    schooleventChannel = client.get_channel(int(882722734398914670))



    embed = discord.Embed(
        title = str(eventInfo['title'] + ' ❗'),
        description = str(eventInfo['description']),
        url=eventInfo['url']
    )
    embed.set_thumbnail(url='https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/twitter/282/speaking-head_1f5e3-fe0f.png')
    if (eventInfo['dateTime'] != "") and (eventInfo['dateTime'] != None):
        embed.add_field(name="Date 📅", value=eventInfo['dateTime'].strftime('%Y %B %a %d, %I:%M %p'), inline=False)

    if (eventInfo['campus'] != "") and (eventInfo['campus'] != []):
        '''
        campusString = ""
        for campus in eventInfo['campus']:
            campusString += (' ' + campus)
        print('campus string ' + campus )
        '''
        print('campus string:' + str(eventInfo['campus']))
        embed.add_field(name="Campus 🏫", value=str(eventInfo['campus']).strip('[]'), inline=False)

    if (eventInfo['notes'] != ""):
        embed.add_field(name="Notes 📝", value=eventInfo['notes'], inline=False)

    if (eventInfo['zoomLink'] != ""):
        embed.add_field(name="Zoom Link 🔗", value=eventInfo['zoomLink'], inline=False)

    if (eventInfo['link'] != ""):
        embed.add_field(name="General Link 🔗", value='[Link given by page](' + eventInfo['link'] + ')', inline=False)

    await schooleventChannel.send(embed=embed)

def getEventInfo(url, driver=None):
    print('\n\n----------------------------------------------------------------')
    eventInfo = {
        "title": "",
        "date": "",
        "time": "",
        "unixTime": 0,
        "campus": [],
        "address": "",
        "googleMaps": "",
        "zoomLink": "",
        "link": "",
        "description": "",
        "notes": "",
        "url": ""
    }
    chrome_options = Options()
    chrome_options.add_argument("--remote-debugging-port=9230")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,20000")
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--allow-running-insecure-content')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--proxy-bypass-list=*")
    chrome_options.add_argument("--proxy-server='direct://'")
    chrome_options.add_argument("--disable-extensions")
    driver = webdriver.Chrome(executable_path='./commands/SPCEvents/chromedriver', options=chrome_options)
    

    # title
    try:

        time.sleep(1)
        driver.set_page_load_timeout(30)
        driver.get(url)

        driver.execute_script("window.resizeTo(1920,20000)")

        driver.save_screenshot("screenshot_" + "page" + "_.png")

        eventInfo['url'] = url


        title = driver.find_element_by_xpath('//div[@class="eventBlock"]')
        title = title.find_element_by_xpath('.//h2').text
        eventInfo['title'] = titlecase(title)
        eventInfo['title'] = eventInfo['title'].replace('Spc', 'SPC')
        eventInfo['title'] = eventInfo['title'].replace('Ii', 'II')
        eventInfo['title'] = eventInfo['title'].replace('Iii', 'III')
        eventInfo['title'] = eventInfo['title'].replace('Sga', 'SGA')
        print('EVENT TITLE: ' + eventInfo['title'])

        # time
        eventTime = driver.find_element_by_xpath('//div[@class="dateTimeBlock"]')
        eventTime = eventTime.find_element_by_xpath('.//time').get_attribute('datetime')
        eventTime = datetime.strptime(eventTime,"%Y-%m-%dT%H:%M:%S.%f0")
        print(eventTime)
        eventInfo['dateTime'] = eventTime
        print('EVENT TIME: ' + str(eventTime.strftime("%c")))
        eventInfo['unixTime'] = int(time.mktime(eventTime.timetuple()))
        print('UNIX TIME: ' + str(eventInfo['unixTime']))

        # campus(s)
        places = driver.find_element_by_xpath('//div[@class="campusBlock"]')
        places = places.find_elements_by_xpath('.//span')
        for place in places:
            place = place.text
            if 'http' in place.lower():     # link in campus
                if 'zoom' in place.lower(): # a full on zoom link in campus
                    eventInfo['zoomLink'] = place
                else:                       # was not a zoom link, so its a general link
                    eventInfo['link'] = place
            else:                           # an actual campus
                if 'zoom' in place.lower():
                    # looking for zoom button
                    try:
                        zoomButton = driver.find_element_by_xpath('//a[@class="spc-dark-blue-button"]')
                        eventInfo['zoomLink'] = zoomButton.get_attribute('href')
                    except:
                        eventInfo["notes"] = "At time of scan, a Zoom link could not be found. Please check the official SPC event page."
                else:
                    place = titlecase(place)
                    place = place.replace('Spc', 'SPC')
                    eventInfo['campus'].append(place)

        # description
        description = driver.find_element_by_xpath('//div[@class="row eventContent"]').text

        try:
            possibleURL = re.search("(?P<url>https?://[^\s]+)", description).group("url")
            if 'zoom' in possibleURL:
                eventInfo['zoomLink'] = possibleURL
                description = description.replace(possibleURL, '')
            else:
                eventInfo['link'] = possibleURL
                description = description.replace(possibleURL, '')
        except:
            pass

        description = " ".join(description.split())
        description = re.sub(r'(\r\n){2,}','\r\n', str(description))

        eventInfo["description"] = description

        # address
        try:
            address = titlecase(driver.find_element_by_xpath('//div[@class="addressBlock"]').text)
            eventInfo["address"] = address
        except:
            pass

        # google maps link
        try:
            googleMapsLink = driver.find_element_by_xpath('//div[@class="google-maps-link"]')
            googleMapsLink = googleMapsLink.find_element_by_xpath('.//a').get_attribute('href')
            eventInfo["googleMaps"] = googleMapsLink
        except:
            pass

        print('URL: ' + str(eventInfo['url']))
        print('CAMPUS: ' + str(eventInfo['campus']))
        print('ZOOM LINK: ' + str(eventInfo['zoomLink']))
        print('GENERAL LINK: ' + str(eventInfo['link']))
        print('DESCRIPTION: ' + str(eventInfo["description"]))
        print('ADDRESS: ' + str(eventInfo['address']))
        print('GOOGLE MAPS LINK: ' + str(eventInfo['googleMaps']))
        print('NOTES: ' + str(eventInfo['notes']))
    except:
        print('ERROR; PAGE DOES NOT EXIST')
        eventInfo = None
    driver.close()
    return eventInfo

async def main(url="https://www.spcollege.edu/events", client=None):

    cacheName = './commands/SPCEvents/cache.txt'
    with open(cacheName) as cache:
        existing = [line.rstrip() for line in cache]

    '''
    this is given the events page and finds
    events and saves them
    '''
    print('Opening cal pickle')
    try:
        pickle_in = open('./commands/SPCEvents/dict.pickle', 'rb')
        cal = pickle.load(pickle_in)
    except:
        print('pickle cal empty, making a new one')
        dict = []
        pickle_out = open('./commands/SPCEvents/dict.pickle', 'wb')
        pickle.dump(dict, pickle_out)
        pickle_out.close()

        pickle_in = open('./commands/SPCEvents/dict.pickle', 'rb')
        cal = pickle.load(pickle_in)

    #print('cal: ' + str(cal))
    chrome_options = Options()
    #chrome_options.headless = True
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,20000")
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--allow-running-insecure-content')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--proxy-bypass-list=*")
    chrome_options.add_argument("--proxy-server='direct://'")
    chrome_options.add_argument("--disable-extensions")
    # chrome_options.headless = True # also works
    driver = webdriver.Chrome(executable_path='./commands/SPCEvents/chromedriver', options=chrome_options)
    driver.get(url)
    driver.implicitly_wait(5)
    #asyncio.sleep(5)
    #driver.save_screenshot("screenshot.png")
    #driver.execute_script("window.scrollTo(0, document.body.scrollHeight);") 
    

    events = driver.find_elements_by_xpath('//div[@class="event-item"]')

    for event in events:
        url = event.find_element_by_xpath('.//a').get_attribute('href')
        print('EVENT URL: ' + str(url))
        try:
            if url not in existing:
                eventInfo = getEventInfo(url=url)

                diff = eventInfo['dateTime'] - datetime.now()
                notice_in_days = 3
                if ((int(diff.days) >= 0) and (int(diff.days) <= notice_in_days)):		# event in time windows
                    print(datetime.now().strftime("%Y-%m-%d %I:%M:%S:%f %p") + ' -> ' + eventInfo['title'] + ' is happening in ' + str(diff.days) + ' days')
                    existing.append(url + '\n')
                    with open(cacheName, 'a+') as cache:
                        cache.write(url + '\n')

                    await postEvent(eventInfo=eventInfo, client=client)
                else:
                    if (int(diff.days) < 0):							# event passed
                        print(datetime.now().strftime("%Y-%m-%d %I:%M:%S:%f %p") + ' -> ' + eventInfo['title'] + ' has already passed (' + str(diff.days) + ' days)... Removing from cal')
                    else:       # in the future
                        print(datetime.now().strftime("%Y-%m-%d %I:%M:%S:%f %p") + ' -> ' + eventInfo['title'] + ' event too far into the future... (' + str(diff.days) + ' days)')
        except:
            pass


    driver.close()

    '''for event in existing:
        eventInfo = getEventInfo(event, driver)
        if eventInfo != None:
            cal.append(eventInfo)
        #print('CAL: ' + str(cal))
        
    print('saving pickle')
    pickle_out = open('./commands/SPCEvents/dict.pickle', 'wb')
    pickle.dump(cal, pickle_out)
    pickle_out.close()
    print('pickle saved')
'''