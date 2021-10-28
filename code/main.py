#! /usr/bin/python3
"""
Kendel Tatsak
7/28/2021
"""


import time
import random
import azapi
import sys


artist = azapi.getRandomArtist()
print(artist[1] + "\n")
arrayOfLinks = azapi.getSongs(artist[0])
#timeToRun = len(arrayOfLinks) * 15 / 60
print("number of songs to scan for artist " + artist[1] + ": " + str(len(arrayOfLinks)))

count = 0
for link in arrayOfLinks:
    song = azapi.getLyrics(link)
    azapi.addToDict(song)
    time.sleep(random.randint(10, 20))
    
    count += 1
    #print("\t" + str(int(count / len(arrayOfLinks) * 100)) + "% complete. " + str((len(arrayOfLinks) - count)) + " songs remaining.", end="\r")
    print(link)

orderedArray = azapi.getOrderedArray()

fileName = azapi.sendToFile(orderedArray, artist[1], len(arrayOfLinks))
gistURL = azapi.postGist(fileName)
azapi.sendTweet(orderedArray, gistURL, artist, len(arrayOfLinks))
