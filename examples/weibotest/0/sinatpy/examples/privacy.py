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
        
    def basicAuth(self, source, username, password):
        self.auth = BasicAuthHandler(username, password)
        self.api = API(self.auth,source=source)
        
    def setToken(self, token, tokenSecret):
        self.auth = OAuthHandler(self.consumer_key, self.consumer_secret)
        self.auth.setToken(token, tokenSecret)
        self.api = API(self.auth)
        
    def get_privacy(self):
        privacy = self.api.get_privacy()
        self.obj = privacy
        ct = self.getAtt("comment")
        dm = self.getAtt("dm")
        real_name = self.getAtt("real_name")
        geo = self.getAtt("geo")
        badge = self.getAtt("badge") 
        print "privacy---"+ str(ct) + str(dm) + str(real_name) + str(geo) + str(badge)
    def update_privacy(self):
        update_privacy = self.api.update_privacy(comment=0)        

test = Test()
test.basicAuth('source', 'username', 'password')
test.get_privacy()
test.update_privacy()
