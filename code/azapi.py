#! /usr/bin/python3
"""
Kendel Tatsak
7/28/2021

module: azapi

Functions
---------

getLyrics(url)
    Get an array of strings containing each word in a song in sequential order.

    Args:
        url: str
            link to the webpage containing the lyrics to a certain song.
            the format of the link is 'https://azlyrics.com/lyrics/artistName/songName.html'
    
    returns:
        list : an array of strings containing each word in a song in sequential order.


getSongs(url)
    Get an array of strings containing links to all of the songs in an Artist's catalog on azlyrics.com. 

    Args:
        url: str
        link to the webpage listing the artist's catalog.
        The format of the link is https://azlyrics.com/firstInitial/artistName.html
            example: https://azlyrics.com/b/beyonce.html

    Returns:
        list : an array of strings containing the links to the artist's songs.


removeSpecialCharactersPlusLower(array)
    Get an array of strings set to lowercase and with common special characters removed.
       
    Args:
        array: list
            array of strings.

    Returns:
        list : an array of strings with some common special characters removed.


addToDict(array)
    Add to global dictionary with key value pairs containing a word and its number of occurances in an array.

    Args:
        array: list
            array of strings.

    Returns:
        NONE


checkIfInMostCommonWordsArray(word)
    Accepts a sring and checks if it exists in constant array FILTEREDWORDS.

    Args:
        word: str
            string to compare against FILTEREDWORDS array.

    Returns:
        Boolean : True if word exists in array, False if it does not exist in array.

getOrderedArray()
    Get 2D array with each element containing the key value pair from global dictionary.
    Array is ordered from high to low using the int in each index.

    Args:
        NONE

    Returns:
        list : a 2D array with each index containing a string and an int.


getRandomArtist()
    Get a link to a webpage containing a random artist's music catalog.
    The format of the link is https://azlyrics.com/firstInitial/artistName.html
        example: https://azlyrics.com/b/beyonce.html

    Args:
        NONE

    Returns:
        list : an array with the url in the [0] index and the name of the artist in the [1] index.


sendToFile(orderedArray, artistName, numSongs)
    create a text file in the directory ..\frequentlyMost\lyrics

    Args:
        orderedArray: list
            a 2D array with each index containing a string and an int.
        
        artistName: str
            the name of the artist.
        
        numSongs: int
            the number of songs scanned.
    
    Returns:
        str : the name of the file created.


postGist(fileName)
    create a post on gist.github.com containing a text file.

    Args:
        fileName: str
            name and location of the file to be uploaded.
    
    Returns:
        str : url to the gist created on gist.github.com


sendTweet(orderedArray, gistURL, artist, numWords)
    Send tweet containing name of artist, number of songs scanned, top 5 words, and link to gist.

    Args:
        orderedArray: list
            2D array of words and ints ordered by the ints in index [][1].
        
        gistURL: str
            link to the gist on gist.github.com.

        artist: str
            name of the artist.
        
        numWords: int
            the number of songs scanned.
    
    Returns:
        NONE


sendErrorEmail(functionName, e)
    Send email containing name of the function where the exception occured and the exception itself.

    Args:
        functionName: str
            name of funciton where the exception occured.

        e: Object Exception
            exception thrown.

    Returns:
        NONE
"""

import re
import requests
import bs4
import random
import json
import tweepy
import sys
import keyring
import time


# global variables
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
                'cause', 'ill', 'itll', 'off', 'im', 'me', 'am', 'yeah', 'oh', '-', '- -',
                'couldve', 'shouldve', 'thatll', 'want', 'wanna', 'la', 'da', 'ba', 'le']


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
        lyrics = removeSpecialCharactersPlusLower(lyrics_tags[0].getText().split())
        return lyrics


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


def removeSpecialCharactersPlusLower(array):
    formattedArray = []
    for word in array:
        if '[' in word or ']' in word:
            pass
        else:
            formattedArray.append(re.sub("\!|\.|\;|\:|\?|\'|\,|\"||\(|\)|&|\’", "", word).lower())

    return formattedArray


def addToDict(array):
    global uniqueWordsDict

    for word in array:
        if checkIfInMostCommonWordsArray(word):
            pass
        elif word not in uniqueWordsDict:
            uniqueWordsDict[word] = 1
        else:
            uniqueWordsDict[word] = uniqueWordsDict[word] + 1


def checkIfInMostCommonWordsArray(word):
        return word in FILTEREDWORDS

    
def getOrderedArray():
    global uniqueWordsDict
    uniqueWordsArray = []

    for word, timesUsed in uniqueWordsDict.items():
        uniqueWordsArray.append([word, timesUsed])
    uniqueWordsArray.sort(key=lambda x: x[1], reverse=True)

    return uniqueWordsArray


def getRandomArtist():
    firstLetters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n',
                    'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '19']
    
    artist = ''
    with open('../artistsToScan.txt', 'r') as file:
        lines = file.read().splitlines()
        if lines != []:
            artist = lines[0].split(',')

    with open('../artistsToScan.txt', 'w') as file:
        i = 0
        if lines != []:
            for line in lines:
                if i is 0:
                    pass
                else:
                    file.writelines(lines[i] + '\n')
                i += 1

    if artist == '':

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

    return artist


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


def sendTweet(orderedArray, gistURL, artist, numWords):
    with open('/etc/tokens.txt', 'r') as file:
        tokens = file.read().splitlines()

    auth = tweepy.OAuthHandler(tokens[1], tokens[2])
    auth.set_access_token(tokens[3], tokens[4])
    api = tweepy.API(auth)
    tweet = ("Top 5 words used by " + artist + "\n"
             "Number of songs scanned: " + str(numWords) + "\n\n"
             "1. " + orderedArray[0][0] + " - " + str(orderedArray[0][1]) + " uses.\n"
             "2. " + orderedArray[1][0] + " - " + str(orderedArray[1][1]) + " uses.\n"
             "3. " + orderedArray[2][0] + " - " + str(orderedArray[2][1]) + " uses.\n"
             "4. " + orderedArray[3][0] + " - " + str(orderedArray[3][1]) + " uses.\n"
             "5. " + orderedArray[4][0] + " - " + str(orderedArray[4][1]) + " uses.\n\n"
             "View the entire list here: " + gistURL
            )

    api.update_status(tweet)


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

