#!/usr/bin/python
#coding=gbk

'''
Created on 2011-2-25

@author: sina(weibo.com)
'''

import unittest
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
        
    def setToken(self, token, tokenSecret):
        self.auth = OAuthHandler(self.consumer_key, self.consumer_secret)
        self.auth.setToken(token, tokenSecret)
        self.api = API(self.auth)
        
    def basicAuth(self, source, username, password):
        self.auth = BasicAuthHandler(username, password)
        self.api = API(self.auth,source=source)
        
    def comments(self):
        comments = self.api.comments(id= 6687160417)
        for comment in comments:
            self.obj = comment
            mid = self.getAtt("id")
            text = self.getAtt("text")
            print "comments---"+ str(mid) +":"+ text
    
    def comments_timeline(self):
        comments = self.api.comments_timeline()
        for comment in comments:
            self.obj = comment
            mid = self.getAtt("id")
            text = self.getAtt("text")
            print "comments_timeline---"+ str(mid) +":"+ text
    
    def comments_by_me(self):
        comments = self.api.comments_by_me()
        for comment in comments:
            self.obj = comment
            mid = self.getAtt("id")
            text = self.getAtt("text")
            print "comments_by_me---"+ str(mid) +":"+ text
        
    def comment(self):
        comment = self.api.comment(id=6687160417, comment='test')
        self.obj = comment
        mid = self.getAtt("id")
        text = self.getAtt("text")
        print "comment---"+ str(mid) +":"+ text
        return mid
    
    def comment_destroy (self, mid):
        comment = self.api.comment_destroy(mid)
        self.obj = comment
        mid = self.getAtt("id")
        text = self.getAtt("text")
        print "comment_destroy---"+ str(mid) +":"+ text

test = Test()
#AccessToken的 key和Secret
test.setToken("key", "secret")
test.comment()


