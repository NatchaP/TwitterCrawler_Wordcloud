
# coding: utf-8

# In[1]:


# - * - coding: UTF-8 - * -
import asyncio
import tweepy
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import MySQLdb
import time
import json
import argparse
import string
import re,os
import os
from os import path
from wordcloud import WordCloud
import re
from threading import Thread
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
stop_words = set(stopwords.words('english')) 

consumer_key = 'xxxx'
consumer_secret = 'xxxx'
access_token = 'xxxx'
access_token_secret = 'xxxx'

conn = MySQLdb.connect("yourConnection","username","password","database", use_unicode=True, charset="utf8")
c = conn.cursor()

#consumer key, consumer secret, access token, access secret.
ckey=consumer_key
csecret=consumer_secret
atoken=access_token
asecret=access_token_secret

class listener(StreamListener):

    def on_data(self, data):
        all_data = json.loads(data)
        
        tweet = all_data["text"]
        tweet = re.sub(r'http\S+', '', tweet)
        tweet = re.sub(r'RT @\S+\:$','',tweet)
        tweet = re.sub('RT @[^\s]+','',tweet)
        tweet = re.sub(r'[^a-zA-Z ]+', '', tweet)
        print(tweet)
        username = all_data["user"]["screen_name"]
        
        #print((username,tweet))
        c.execute("INSERT INTO tweets (username, tweet) VALUES (%s,%s)",(username, tweet))

        conn.commit()

        
        
        return True

    def on_error(self, status):
        print (status)
        
    def streamTwitter(self):
        auth = OAuthHandler(ckey, csecret)
        auth.set_access_token(atoken, asecret)

        twitterStream = Stream(auth, listener())
        twitterStream.filter(languages=["en"], track=["Bird Box"]) #ถ้าจาก Hashtag ให้ใส่ # ถ้าคำธรรมดา ไม่ต้องใส่ก็ได้ 
        #https://developer.twitter.com/en/docs/tweets/rules-and-filtering/overview/standard-operators.html
        
    
    def selectData(self):
        d = path.dirname(__file__) if "__file__" in locals() else os.getcwd()

        text = ""

        conn = MySQLdb.connect("localhost","root","intranet","tweet", use_unicode=True, charset="utf8")
        c = conn.cursor()

        c.execute("SELECT tweet FROM tweets")

        myresult = c.fetchall()
        #print (type(myresult))
        for x in myresult:
            #print(x[0])
            text = text +" "+ x[0]
        
        from nltk.tokenize import word_tokenize 
        text = text.lower()
        word_tokens = word_tokenize(text) 
        filter_text = [w for w in word_tokens if not w in stop_words] 
        filter_text = []
        for w in word_tokens:
            if w not in stop_words: 
                filter_text.append(w)
        text = ""
        for s in filter_text:
            text = text+" "+s
        
        return text
    
    def genWC(self):
        b =  listener()
        text = b.selectData()
        print(text)
        # Generate a word cloud image
        wordcloud = WordCloud().generate(text)

        # Display the generated image:
        # the matplotlib way:
        import matplotlib.pyplot as plt
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        plt.show(block=False)
        plt.pause(5)
        plt.close()
        
        #wordcloud = WordCloud(max_font_size=40).generate(text)
        #plt.figure()
        #plt.imshow(wordcloud, interpolation="bilinear")
        #plt.axis("off")


# In[2]:


async def myCoroutine():
    timeout = time.time() + 60*5
    while(time.time() < timeout):
        a = listener()
        a.genWC()
        await asyncio.sleep(1)
    #a.streamTwitter()

def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(myCoroutine())
    loop.close()

if __name__ == '__main__':
    main()
    
#if __name__ == '__main__':
#    a = listener()
#    Thread(target = a.genWC()).start()
#    Thread(target = a.streamTwitter()).start()
    

