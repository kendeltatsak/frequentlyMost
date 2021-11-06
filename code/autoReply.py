#! /usr/bin/python3

# Kendel Tatsak
# 7/28/2021


import tweepy
import sqlite3
import datetime as dt
import pytz
from AzlyricsAPI import AzlyricsAPI
from AzlyricsAPI import Artist


class Tweet:
    def __init__(self, status):
        self.id = status[0]
        self.str_id = status[1]
        self.created_at = dt.datetime.fromisoformat(status[2])
        self.at_user = status[3]
        self.text = status[4]
        self.user = status[5]
        self.num_replies = status[6]
    
        
    def get_all(self):
        return ([self.id, self.str_id, self.created_at, self.at_user, self.text,
                 self.user, self.num_replies])


class Database:
    
    DB_FILE = '../tweets.db'
    
    @classmethod
    def selectFromDB(cls, sqlCode):
        conn = sqlite3.connect(cls.DB_FILE)
        
        with conn:
            c = conn.cursor()
            c.execute(sqlCode)
        
        return Tweet(c.fetchall()[0])
    
    @classmethod
    def updateDB(cls, tweet, sqlCode):
        conn = sqlite3.connect(cls.DB_FILE)
        
        with conn:
            c = conn.cursor()
            c.execute(sqlCode)

if __name__ == '__main__':
    
    try:
    
        api = AzlyricsAPI.twitterLogin()
        statuses = api.home_timeline()
        
        for status in statuses:
            if str(status.user.screen_name) != 'frequentlyMost':
                
                
                sqlCode = f"SELECT * FROM tweets WHERE LOWER(at_user) LIKE LOWER('%{status.user.screen_name}%')"
                tweet = Database.selectFromDB(sqlCode)
                
                
                timeElapsed = dt.datetime.utcnow().replace(tzinfo=pytz.utc) - status.created_at
                
                
                if timeElapsed.seconds < 300 and tweet.num_replies < 4:
                    
                    replyTweet = f"https://twitter.com/{tweet.user}/status/{tweet.str_id}"
                    api.update_status(status=replyTweet, in_reply_to_status_id = status.id_str,
                                      auto_populate_reply_metadata=True)
                    
                    
                    sqlCode = f"""UPDATE tweets
                                  SET num_replies = {tweet.num_replies + 1}
                                  WHERE id = {tweet.id}"""
                    Database.updateDB(tweet, sqlCode)
                    
                    
                    print(f"replied to {status.user.screen_name} with tweet id {tweet.str_id} at {dt.datetime.utcnow()} UTC+00:00.") 
    
    except Exception as e:
        print(e)
    
    
    
    
    
    
    
    
    
    
    
    
    
