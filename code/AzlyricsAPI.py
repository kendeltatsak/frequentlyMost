#! /usr/bin/python3

# Kendel Tatsak
# 7/28/2021


import re
import requests
import bs4
import random
import json
import tweepy
import sys
import keyring
import time
import sqlite3
import datetime


class AzlyricsAPI:
    
    uniqueWordsDict = {}
    FILTEREDWORDS = ['the', 'of', 'and', 'a', 'to', 'in', 'is', 'you', 'that', 'it', 'he', 'thats',
                    'was', 'for', 'on', 'are', 'as', 'with', 'his', 'they', 'i', 'at', 'be', 'know', 
                    'this', 'have', 'from', 'or', 'one', 'had', 'by', 'word', 'but', 'not', 'aint',
                    'what', 'all', 'were', 'we', 'when', 'your', 'can', 'said', 'there', 'use', 'man',
                    'an', 'each', 'which', 'she', 'do', 'how', 'their', 'if', 'will', 'up', 'say', 'id', 
                    'out', 'many', 'then', 'them', 'these', 'so', 'some', 'our', 'youll', 'where', 'theyre',
                    'her', 'would', 'make', 'like', 'him', 'into', 'time', 'has', 'look', 'youve', 'theres',
                    'two', 'more', 'go', 'see', 'no', 'way', 'could', 'just', 'cause', 'got', 'theyve',
                    'still', 'my', 'than', 'gonna', 'been', 'call', 'who', 'hes', 'shes', 'whos',
                    'its', 'now', 'find', 'day', 'did', 'get', 'come', 'made', 'us', 'our', 'well',
                    'may', 'part', 'dont', 'youre', 'too', 'didnt', 'ive', 'why', 'cant', 'wont',
                    'cause', 'ill', 'itll', 'off', 'im', 'me', 'am', 'yeah', 'oh', '-', '- -', '– -',
                    'couldve', 'shouldve', 'thatll', 'want', 'wanna', 'la', 'da', 'ba', 'le', 'ok']
    
    
    @classmethod
    def checkIfInMostCommonWordsArray(cls, word):
        return word in cls.FILTEREDWORDS
    
    
    @classmethod
    def addToDict(cls, array):
        for word in array:
            if cls.checkIfInMostCommonWordsArray(word):
                pass
            elif word not in cls.uniqueWordsDict:
                cls.uniqueWordsDict[word] = 1
            else:
                cls.uniqueWordsDict[word] = cls.uniqueWordsDict[word] + 1
                
                
    @staticmethod
    def getRandomArtist():
        firstLetters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n',
                        'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '19']
        
        artist = None
        # get first line from text file
        with open('../artistsToScan.txt', 'r') as file:
            lines = file.read().splitlines()
            if lines and lines[0] is not '':
                artist = lines[0].split(',')

        # delete first line from text file
        with open('../artistsToScan.txt', 'w') as file:
            i = 0
            if lines and lines[0] is not '':
                for line in lines:
                    if i == 0:
                        pass
                    else:
                        file.writelines(lines[i] + '\n')
                    i += 1
                    
        # if text file is blank, get random artist from azlyrics.com
        if not artist:

            baseUrl = 'https://azlyrics.com/'
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
            response = requests.get(baseUrl + firstLetters[random.randint(0, len(firstLetters)-1)] + '.html', headers=headers)
            
            if response.status_code != 200:
                sendErrorEmail('getRandomArtist()', response.status_code)
            else:
                soup = bs4.BeautifulSoup(response.content, 'html.parser')
                result = soup.select('.row a')

                arrayOfArtists = []
                for i in result:
                    arrayOfArtists.extend([[baseUrl + i.get('href'), i.getText()]])

                artist = arrayOfArtists[random.randint(0, len(arrayOfArtists)-1)]
        
        return Artist(artist[0], artist[1]) if len(artist) is 2 else Artist(artist[0], artist[1], artist[2])
    
    
    @staticmethod
    def getSongs(url):
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        mainPage = requests.get(url=url, headers=headers)
        if mainPage.status_code != 200:
            sendErrorEmail('getSongs()', mainPage.status_code)
        else:
            soup = bs4.BeautifulSoup(mainPage.content, "html.parser")
            songs = soup.select('.listalbum-item > a')

            arrayLinksToArtistsSongs = []
            for song in songs:
                arrayLinksToArtistsSongs.append([song.get('href')][0].replace("..", "https://azlyrics.com"))
            
            random.shuffle(arrayLinksToArtistsSongs)
            return list(set(arrayLinksToArtistsSongs))
        
        
    @staticmethod
    def getLyrics(url):
        mainPage = None
        retryCount = 0
        while mainPage is None:
            if retryCount is 11:
                sendErrorEmail('Error in getLyrics(). Retry count exceeded 10 tries.', retryCount)
            else:
                try:
                    mainPage = requests.get(url)
                except:
                    print("connection error. Retrying in 20 seconds.")
                    time.sleep(20)
                    retryCount += 1
                
        if mainPage.status_code != 200:
            sendErrorEmail('getLyrics()', mainPage.status_code)
        else:
            soup = bs4.BeautifulSoup(mainPage.content, 'html.parser')
            lyrics_tags = soup.find_all("div", attrs={"class": None, "id": None})
            lyrics = AzlyricsAPI.removeSpecialCharactersPlusLower(lyrics_tags[0].getText().split())
            return lyrics
        
        
    @staticmethod
    def removeSpecialCharactersPlusLower(array):
        formattedArray = []
        for word in array:
            if '[' in word or ']' in word:
                pass
            else:
                formattedArray.append(re.sub("\!|\.|\;|\:|\?|\'|\,|\"||\(|\)|&|\’", "", word).lower())

        return formattedArray
    
    
    @classmethod
    def getOrderedArray(cls):
        uniqueWordsArray = []

        for word, timesUsed in cls.uniqueWordsDict.items():
            uniqueWordsArray.append([word, timesUsed])
        uniqueWordsArray.sort(key=lambda x: x[1], reverse=True)

        return uniqueWordsArray
    
    
    @staticmethod   
    def sendToFile(orderedArray, artistName, numSongs):
        fileName = artistName.replace(" ", "") + '.txt'

        with open('../lyrics/' + fileName, 'w', encoding='utf-8') as file:
            file.write('Most used words by ' + artistName + ': \n')
            file.write('Number of songs scanned: ' + str(numSongs) + '\n\n')
            for i in range(len(orderedArray)):
                line = str(i + 1) + '. ' + str(orderedArray[i][0]) + ' - ' + str(orderedArray[i][1])
                
                if orderedArray[i][1] is 1:
                    line = line + ' use.\n'
                else:
                    line = line + ' uses.\n'
                file.write(line)

        file.close()
        return fileName
    
    
    @staticmethod
    def postGist(fileName):
        url = "https://api.github.com/gists"
        with open('/etc/tokens.txt', 'r') as file:
            tokens = file.read().splitlines()

        headers = {'Authorization': 'token ' + tokens[0]}
        content = open('../lyrics/' + fileName, 'r').read()
        data = {
            "public": True,
            "files": {
                fileName: {
                    "content": content
                }
            }    
        }

        r = requests.post(url=url, headers=headers, data=json.dumps(data))
        return r.json()['html_url']
    
    
    @staticmethod
    def twitterLogin():
        with open('/etc/tokens.txt', 'r') as file:
            tokens = file.read().splitlines()

        auth = tweepy.OAuthHandler(tokens[1], tokens[2])
        auth.set_access_token(tokens[3], tokens[4])
        
        return tweepy.API(auth)
    
    @staticmethod
    def sendTweet(api, orderedArray, gistURL, artist, numWords):
        if artist.get_handle():
            tweet = ("Top 5 words used by " + artist.get_name() + "\n"
                     "(@" + artist.get_handle() + ")" + "\n\n"
                     "1. " + orderedArray[0][0] + " - " + str(orderedArray[0][1]) + " uses.\n"
                     "2. " + orderedArray[1][0] + " - " + str(orderedArray[1][1]) + " uses.\n"
                     "3. " + orderedArray[2][0] + " - " + str(orderedArray[2][1]) + " uses.\n"
                     "4. " + orderedArray[3][0] + " - " + str(orderedArray[3][1]) + " uses.\n"
                     "5. " + orderedArray[4][0] + " - " + str(orderedArray[4][1]) + " uses.\n\n"
                     "View the entire list here: " + gistURL
                    )
        else:
            tweet = ("Top 5 words used by " + artist.get_name() + "\n\n"
                     "1. " + orderedArray[0][0] + " - " + str(orderedArray[0][1]) + " uses.\n"
                     "2. " + orderedArray[1][0] + " - " + str(orderedArray[1][1]) + " uses.\n"
                     "3. " + orderedArray[2][0] + " - " + str(orderedArray[2][1]) + " uses.\n"
                     "4. " + orderedArray[3][0] + " - " + str(orderedArray[3][1]) + " uses.\n"
                     "5. " + orderedArray[4][0] + " - " + str(orderedArray[4][1]) + " uses.\n\n"
                     "View the entire list here: " + gistURL
                )
        
        return api.update_status(tweet)
        
        
    @staticmethod
    def followUser(artist, api):
        api.create_friendship(screen_name=artist.get_handle())
        
        
    @staticmethod
    def createDatabase():
        conn = sqlite3.connect('../tweets.db')
        c = conn.cursor()
        sqlCode = ("""
                CREATE TABLE tweets (
                id INTEGER PRIMARY KEY,
                id_str TEXT,
                created_at TEXT,
                at_user TEXT,
                text TEXT,
                user TEXT,
                num_replies INT
                )
                """)
        
        c.execute(sqlCode)
        conn.commit()
        conn.close()
        
        
    @staticmethod
    def addToDatabase(tweet, artist):
        conn = sqlite3.connect('../tweets.db')
        c = conn.cursor()
        sqlCode = f"""
                INSERT INTO tweets (id_str, created_at, at_user, text, user, num_replies)
                VALUES ('{tweet.id_str}', '{str(tweet.created_at).strip('+00:00')}',
                '{artist.get_handle()}','{tweet.text}', '{tweet.user.screen_name}', 0)
                """
        
        c.execute(sqlCode)
        conn.commit()
        conn.close()
            
    
    @staticmethod
    def sendErrorEmail(functionName, e):

        # TODO configure automated emails through gmail

        if type(e) == int:
            message = 'error in ' + functionName + '. Error: HTTP status code returned == ' + str(e)
            print(message)
            sys.exit(message)
        else:
            message = 'error in ' + functionName + '. Error:\n\n' + str(e)
            print(message)
            sys.exit(message)
                    

class Artist(AzlyricsAPI):
    def __init__(self, url, name, handle=None):
        self.url = url
        self.name = name
        self.handle = handle
    
    def get_url(self):
        return self.url
    
    def get_name(self):
        return self.name
    
    def get_handle(self):
        return self.handle
    
    def get_all(self):
        return [self.url, self.name, self.handle]
    

if __name__ == '__main__':
    
    artist = AzlyricsAPI.getRandomArtist()
    print(artist.get_all())
    arrayOfLinks = AzlyricsAPI.getSongs(artist.get_url())
    print("number of songs to scan for artist " + artist.get_name() + ": " + str(len(arrayOfLinks)))
 
    count = 0
    for link in arrayOfLinks:
        song = AzlyricsAPI.getLyrics(link)
        AzlyricsAPI.addToDict(song)
        time.sleep(random.randint(10, 20))
        
        count += 1
        print(str(count) + " of " + str(len(arrayOfLinks)) + ": " + link)

    orderedArray = AzlyricsAPI.getOrderedArray()

    fileName = AzlyricsAPI.sendToFile(orderedArray, artist.get_name(), len(arrayOfLinks))
    gistURL = AzlyricsAPI.postGist(fileName)
    
    api = AzlyricsAPI.twitterLogin()
    tweet = AzlyricsAPI.sendTweet(api, orderedArray, gistURL, artist, len(arrayOfLinks))
    
    
    if artist.get_handle():
        AzlyricsAPI.followUser(artist, api)
        print("followed: " + artist.get_handle())
        AzlyricsAPI.addToDatabase(tweet, artist)
        print("added tweet to database")
    
            

    
#     artist = AzlyricsAPI.getRandomArtist()
#     api = AzlyricsAPI.twitterLogin()
#     statuses = api.home_timeline()
#     print(type(statuses[0].created_at))

    
    
    

