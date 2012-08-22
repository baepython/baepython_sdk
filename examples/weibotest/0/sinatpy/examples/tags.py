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
        self.authType = 'basicauth'
        self.auth = BasicAuthHandler(username, password)
        self.api = API(self.auth,source=source)        
    def setToken(self, token, tokenSecret):
        self.auth = OAuthHandler(self.consumer_key, self.consumer_secret)
        self.auth.setToken(token, tokenSecret)
        self.api = API(self.auth)
    def tags(self):
        tags = self.api.tags(user_id=1377583044)
        for line in tags:
            self.obj = line
            tagid=self.getAtt("id")
            value = self.getAtt(tagid)
            print tagid,value
    def tag_create(self ,message):
        message = message.encode("utf-8")
        tag_create = self.api.tag_create(tags=message)
        for line in tag_create:
            self.obj = line
            tagid = self.getAtt("tagid")
            print "tag_create---"+tagid
    def tag_suggestions(self):
        tag_suggestions=self.api.tag_suggestions()
        for line in tag_suggestions:
            self.obj = line
            id = self.getAtt("id")
            value = self.getAtt("value")
            print "tag_suggestions---"+ id +":"+ value
    def tag_destroy(self,tag_id):
        tag_destroy=self.api.tag_destroy(tag_id)
        self.obj=tag_destroy
        result=self.getAtt("result")
        print "tag_destroy---"+ result
    def tag_destroy_batch(self,tag_ids):
        tag_destroy_batch=self.api.tag_destroy_batch(tag_ids)
        for line in tag_destroy_batch:
            self.obj = line
            tagid=self.getAtt("tagid")
            print "tag_destroy_batch---"+ tagid                        
    
test=Test()
test.setToken('key','secret')
test.tags()