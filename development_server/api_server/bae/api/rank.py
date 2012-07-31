import os
import copy
import time as t
import pickle

MAX_NAME_LEN = 128
MAX_RANK =  100
MAX_ITEM_NUM = 10000
MAX_INT = 2**31-1
MIN_INT = -2**31

RETURN = {u'request_id' : 0}

class BaeRankManager(object):
    @staticmethod
    def getInstance(*args):
        return BaeRankManager(*args)
    
    def __init__(self, *args):
        self._cache = [] #(rname, BaeRank) 

    def __del__(self):
        with open(os.path.join(os.environ['APP_ROOT'], 'rankmgr.data.'+t.strftime("%Y%m%d%H%M%S")), 'w+') as f:
            pickle.dump(self._cache, f)

    def create(self, rname, keylimit, **kwargs):
        if len(rname) > MAX_NAME_LEN or rname in self._cache:
            raise Exception
        try:
            keylimit = int(keylimit)
        except:
            raise Exception
        kws = {'order': 0, 'expire_time': 0, 'keylimit': keylimit}
        if 'expire_time' in kwargs:
            if kwargs['expire_time'] < 0:
                raise Exception
            try:
                kws['expire_time'] = int(kwargs.pop('expire_time'))*60
            except: pass
        if kws['expire_time'] > 0:    
            kws['expire_time'] += t.time()
        kws.update(kwargs)
        obj = BaeRank(**kws)
        self._cache.append((rname, obj))
        return obj
    
    def getList(self, start = 0, limit = 10):
        if start < 0 or limit <= 0:
            raise Exception
        ret =  copy.deepcopy(RETURN)
        ranks = {}
        for n, o in self._cache[start:(start+limit)]:
            if o._expire > 0 and o._expire < t.time():
                o._cache = {}
                o._sorted = []
            ranks[n] = {u'key_limit': o._keylimit,
                        u'expire_time': o._expire,
                        u'create_time': 0,
                        u'next_expire_time': 0,
                        u'key_num': len(o._cache),
                        u'order': 0 if o._order else 1}
        ret.update({u'response_params': {u'ranks': ranks, u'total_num': len(self._cache)}})
        return ret

    def isExist(self, rname):
        if len(rname) > MAX_NAME_LEN:
            raise Exception
        if rname in [i[0] for i in self._cache]:
            return True
        return False

    def remove(self, rname):
        if len(rname) > MAX_NAME_LEN or rname not in [i[0] for i in self._cache]:
            raise Exception 
        for i in range(len(self._cache)):
            if self._cache[i][0] == rname:
                self._cache[i][1]._removed = True
                self._cache.pop(i)
                break
        return copy.deepcopy(RETURN)

def decorator(func):
    def wrap(*args, **kwargs):
        if getattr(args[0], '_removed'):
            raise Exception
        f = lambda x: x > 0 and x < t.time()
        if f(getattr(args[0], '_expire')):
            setattr(args[0], '_cache', {})
            setattr(args[0], '_sorted', [])
        return func(*args, **kwargs)
    return wrap

class BaeRank(object):
    def __init__(self, *args, **kwargs):
        self._cache = {} #{key: value}    
        self._order = False if kwargs['order'] else True
        self._expire = kwargs['expire_time']
        self._keylimit = kwargs['keylimit']
        self._sorted = []      
        self._removed = False

    def __del__(self):
        with open(os.path.join(os.environ['APP_ROOT'], 'rank.data.'+t.strftime("%Y%m%d%H%M%S")), 'w+') as f:
            pickle.dump(self._cache, f)

    def _get(self, cmd, key, value = None):
        if len(key) > MAX_NAME_LEN or key not in self._cache:
            raise Exception
        ret = copy.deepcopy(RETURN)
        if cmd == 'get':
            _rank = self._sorted.index(key)
            ret.update({u'response_params': {u'value': self._cache[key], u'rank': _rank}})
            return ret    
        if cmd == 'incr':
            try:
                self._cache[key] += int(value)
            except: pass
        if cmd == 'decr':
            try:
                self._cache[key] -= int(value)
            except: pass
        if self._cache[key] > MAX_INT:
            self._cache[key] = MAX_INT 
        if self._cache[key] < MIN_INT:
            self._cache[key] = MIN_INT
        ret.update({u'response_params': {u'value': self._cache[key]}})
        return ret        
    
    @decorator    
    def set(self, **kwargs):
        if len(self._cache) + 1 > self._keylimit or any(map(lambda x: len(x) > MAX_NAME_LEN, kwargs.keys())):
            raise Exception
        try:
            for k, v in kwargs.items():
                self._cache[k] = int(v) 
                if self._cache[k] > MAX_INT:
                    self._cache[k] = MAX_INT
                if self._cache[k] < MIN_INT:
                    self._cache[k] = MIN_INT
                self._sorted.append(k)
        except: 
            raise Exception
        self._sorted.sort(key = lambda x: self._cache[x], reverse = self._order)        
        return copy.deepcopy(RETURN)

    @decorator    
    def get(self, key):
        return self._get('get', key)        
    
    @decorator    
    def increase(self, key, value = 1):  
        return self._get('incr', key, value)        

    @decorator    
    def decrease(self, key, value = 1):
        return self._get('decr', key, value)        

    @decorator    
    def remove(self, key):
        if len(key) > MAX_NAME_LEN or key not in self._cache:
            raise Exception
        self._cache.pop(key)
        self._sorted.remove(key)
        return copy.deepcopy(RETURN)

    @decorator    
    def getList(self, start = 0, limit = 10):
        if start < 0 or limit <= 0:
            raise Exception
        return [(unicode(i), self._cache[i]) for i in self._sorted[start:(start+limit)]]
    
    @decorator    
    def query(self):
        ret = copy.deepcopy(RETURN)
        key_num = len(self._cache)
        ret.update({u'response_params': {u'expire_time': self._expire, 
                                         u'create_time': 0, 
                                         u'next_expire_time': 0, 
                                         u'key_num': key_num, 
                                         u'key_limit': self._keylimit, 
                                         u'order': 0 if self._order else 1}})
        return ret

    @decorator    
    def clear(self):           
        self._cache = {}
        self._sorted = []
        return copy.deepcopy(RETURN)
              
