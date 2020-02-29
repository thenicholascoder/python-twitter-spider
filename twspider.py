# from urllib library, import urlopen, urllib.error
from urllib.request import urlopen
import urllib.error

# import twurl json sqlite3 ssl libraries
import twurl
import json
import sqlite3
import ssl

# twitter base url talking to api
TWITTER_URL = 'https://api.twitter.com/1.1/friends/list.json'

# create database
# IF spider.sqlite doesn't exist, then sqlite3 will create it
conn = sqlite3.connect('spider.sqlite')

# We get ourselves a cursor
cur = conn.cursor()

# We are going to do a create table if not exist
# spidering process
cur.execute('''
            CREATE TABLE IF NOT EXISTS Twitter
            (name TEXT, retrieved INTEGER, friends INTEGER)''')

# Python will ignore SSL certificate errors because of the ssl library
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Indefinite loop
while True:

    # Enter an input account
    acct = input('Enter a Twitter account, or quit: ')

    # if acct == quit, break
    if (acct == 'quit'): break
    
    # if the length is less than < 1
    if (len(acct) < 1):

        # we will read-grab from the database an unretrieved Twitter person, then grab friends
        cur.execute('SELECT name FROM Twitter WHERE retrieved = 0 LIMIT 1')

        try:
            # cur.fetchone() = fetch one row from database
            acct = cur.fetchone()[0]

        except:
            # they will retrieve twitter accounts
            print('No unretrieved Twitter accounts found')
            continue

    # this twurl.augment requires hidden.py file which has keys and secrets in it
    # screen name = 5, count =5 because we are just going to get 5
    url = twurl.augment(TWITTER_URL, {'screen_name': acct, 'count': '5'})

    # Print Retriving then show url
    print('Retrieving', url)

    # File handler
    connection = urlopen(url, context=ctx)

    # Read the FH then decode from UTF-8 to Unicode
    data = connection.read().decode()

    # We will ask for headers
    headers = dict(connection.getheaders())

    # Print Remaining then show headers which has a key of x-rate-limit-remaining
    print('Remaining', headers['x-rate-limit-remaining'])

    # json.loads means load string from data
    js = json.loads(data)

    # Debugging
    # print json.dumps(js, indent=4)

    # FIRST THING
    # update the database
    # then change the retrieved from "0" to "1"
    cur.execute('UPDATE Twitter SET retrieved=1 WHERE name = ?', (acct, ))

    # variables
    countnew = 0
    countold = 0

    # for each js with [users] index LIST
    for u in js['users']:

        # get the each data with key of [screen_name] then assign it to friend
        friend = u['screen_name']

        # print the result
        print(friend)

        # cur.execute means use the database
        # select friends from Twitter table where name = friend which is the u['screen_name']
        cur.execute('SELECT friends FROM Twitter WHERE name = ? LIMIT 1',
                    (friend, ))

        # try except
        try:

            # cur.fetchone()[0] means get the first row on database first box
            count = cur.fetchone()[0]

            # cur.execute = use database sql
            # execute Update Twitter table 
            # SET friends = count+1
            # WHERE name = friend
            cur.execute('UPDATE Twitter SET friends = ? WHERE name = ?',
                        (count+1, friend))

            # update value of countold value
            countold = countold + 1

        # if try blows up, this will run
        except:

            # cur.execture = use database
            # insert into table = Twitter
            # name = ? = friend
            # retrieved = 0
            # friends = 1
            cur.execute('''INSERT INTO Twitter (name, retrieved, friends)
                        VALUES (?, 0, 1)''', (friend, ))

            # update value of countnew
            countnew = countnew + 1

    # print how many value variable has
    print('New accounts=', countnew, ' revisited=', countold)

    # commit the transaction
    conn.commit()

# close the database
cur.close()
