#!/usr/bin/python
#coding=gbk

'''
Created on 2011-2-25

@author: sina(weibo.com)
'''

from weibopy.models import Trends

import unittest
import time
from weibopy.auth import OAuthHandler, BasicAuthHandler
from weibopy.api import API

class Test(unittest.TestCase):
    
    consumer_key= ""
    consumer_secret =""
    
    def __init__(self):
            """ constructor """
    
    def getAtt(self, key):
        try:
            return self.obj.__getattribute__(key)
        except Exception, e:
            print e
            return ''
        
    def getAttValue(self, obj, key):
        try:
            return obj.__getattribute__(key)
        except Exception, e:
            print e
            return ''
        
    def auth(self):
        self.auth = OAuthHandler(self.consumer_key, self.consumer_secret)
        auth_url = self.auth.get_authorization_url()
        print 'Please authorize: ' + auth_url
        verifier = raw_input('PIN: ').strip()
        self.auth.get_access_token(verifier)
        self.api = API(self.auth)
    def basicAuth(self, source, username, password):
        self.authType = 'basicauth'
        self.auth = BasicAuthHandler(username, password)
        self.api = API(self.auth,source=source)        
    def setToken(self, token, tokenSecret):
        self.auth = OAuthHandler(self.consumer_key, self.consumer_secret)
        self.auth.setToken(token, tokenSecret)
        self.api = API(self.auth)
    
    def trends(self):
        trends = self.api.trends(user_id=1377583044,count=20, page=1)
#        print str(len(trends))
        for line in trends:
            self.obj=line
            num = self.getAtt("num")
            trend_id = self.getAtt("trend_id")
            hotword = self.getAtt("hotword")
            print "trends---"+ num +":"+ hotword +":"+trend_id
    def trends_statuses(self , message):
        message = message.encode("utf-8")
        trends_statuses = self.api.trends_statuses(message)
        for line in trends_statuses:
            self.obj=line
            id = self.getAtt("id")
            text = self.getAtt("text")
            print "ToReader---"+ str(id) + ":" +text
#            print text 
    def trends_follow(self , message):
        message = message.encode("utf-8")
        trends_follow = self.api.trends_follow(message)
    def trends_destroy(self , id):
        trends_destroy=self.api.trends_destroy(id)
    def trends_hourly(self):
        trends_hourly = self.api.trends_hourly(base_app=0)
        self.obj=trends_hourly
        query = self.getAtt("trends")
        as_of = self.getAtt("as_of")
        for key in query:
            key = time.strftime('%Y-%m-%d',time.localtime(as_of))
            for line in query[key]:
                query = line["query"]
                name = line["name"]
                print "trends_hourly---"+"Query:" + query+",Name:"+ name
    def trends_daily(self):
        trends_daily=self.api.trends_daily(base_app=0)
        self.obj=trends_daily
        query=self.getAtt("trends")
        as_of=self.getAtt("as_of")
        for key in query:
            key=time.strftime('%Y-%m-%d',time.localtime(as_of))
            for line in query[key]:
                query=line["query"]
                name=line["name"]
                print "trends_daily---"+"Query:" + query+",Name:"+ name   
    def trends_weekly(self):
        trends_weekly=self.api.trends_weekly(base_app=0)
        self.obj=trends_weekly
        query=self.getAtt("trends")
        as_of=self.getAtt("as_of")
        for key in query:
            key = time.strftime('%Y-%m-%d',time.localtime(as_of))
            for line in query[key]:
                query=line["query"]
                name=line["name"]  
                print "trends_weekly---"+"Query:" + query+",Name:"+ name   
test=Test()
#AccessToken的 key和Secret
test.setToken('key','secret')
test.trends()
test.trends_hourly()
test.trends_daily()
test.trends_weekly()

        
        
        
        
        