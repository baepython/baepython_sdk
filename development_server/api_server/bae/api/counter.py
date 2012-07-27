import os
import pickle
import copy
import time as t

MAX_NAME_LEN = 128
MAX_COUNTER =  200
MAX_INT = 2**63-1
MIN_INT = -2**63

RETURN = {u'request_id' : 0}

class BaeCounter(object):
    def __init__(self, *args):
        self._cache = {} #{cname: cvalue}    
        self._sorted = []        

    def __del__(self):
        with open(os.path.join(os.environ['APP_ROOT'], 'counter.data.'+t.strftime("%Y%m%d%H%M%S")), 'w+') as f:
            pickle.dump(self._cache, f)
            
    def _get(self, cmd, key, value = None):
        if len(key) > MAX_NAME_LEN or key not in self._cache:
            raise Exception
        if cmd == 'incr':
            try:
                self._cache[key] += int(value)
            except: pass
        if cmd == 'decr':
            try:
                self._cache[key] -= int(value)
            except: pass
        if self._cache[key] > MAX_INT or self._cache[key] < MIN_INT:
            raise Exception
        ret = copy.deepcopy(RETURN)
        ret.update({u'response_params': {unicode(key): self._cache[key]}}) 
        return ret        
 
    def register(self, cname):
        if len(cname) > MAX_NAME_LEN or len(self._cache) > MAX_COUNTER or cname in self._cache:
            raise Exception
        self._cache[cname] = 0
        self._sorted.append(cname)
        return copy.deepcopy(RETURN)

    def isExist(self, cname):
        if len(key) > MAX_NAME_LEN:
            raise Exception
        if cname in self._cache:
            return True
        return False
         
    def set(self, cname, cvalue):
        if len(cname) > MAX_NAME_LEN or cname not in self._cache:
            raise Exception
        try:
            self._cache[cname] = int(cvalue) 
        except: pass
        if self._cache[cname] > MAX_INT:
            self._cache[cname] = MAX_INT
        if self._cache[cname] < MIN_INT:
            self._cache[cname] = MIN_INT
        ret = copy.deepcopy(RETURN)
        ret.update({u'response_params': {unicode(cname): self._cache[cname]}})
        return ret

    def get(self, cname):
        return self._get('get', cname)        
    
    def increase(self, cname, cvalue = 1):  
        return self._get('incr', cname, cvalue)        

    def decrease(self, cname, cvalue = 1):
        return self._get('decr', cname, cvalue)        

    def remove(self, cname):
        if len(cname) > MAX_NAME_LEN or cname not in self._cache:
            raise Exception
        self._cache.pop(cname)
        self._sorted.remove(cname)
        return copy.deepcopy(RETURN)

    def getList(self, start = 0, limit = 10):
        if start < 0 or limit <= 0:
            raise Exception
        counters = {}
        for i in self._sorted[start:limit]:
            counters[unicode(i)] = self._cache[i]
        ret = copy.deepcopy(RETURN)
        ret.update({u'response_params': {u'total_num': len(self._cache), u'counters':counters}})
        return ret    
                        
