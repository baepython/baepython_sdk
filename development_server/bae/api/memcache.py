import os
import pickle
import time as t

MAX_KEY = 180
MAX_VALUE = 1024*1024
MAX_MULTI = 60
MAX_INT = 2**63-1
MIN_INT = -2**63

class BaeMemcache(object):
    @staticmethod
    def countable(v):
        ret = False
        if isinstance(v, int) or isinstance(v, long):
            ret = True
        if isinstance(v, str) and (v.isdigit() or (len(v) > 0 and v[0] == '-' and v[1:].isdigit())):
            ret = True    
        return ret
        
    def __init__(self, servers = []):
        self.servers = servers
        self._cache = {} #{key: (value, expire)}
  
    def __del__(self):
        with open(os.path.join(os.environ['APP_ROOT'], 'memcache.data.'+t.strftime("%Y%m%d%H%M%S")), 'w+') as f:
            pickle.dump(self._cache, f)
 
    def _set(self, cmd, key, vals, time): #vals: (values, creat_time) 
        value = vals[0]
        if self.countable(value):
            value = str(value)
        value_len = len(pickle.dumps(value)) if not isinstance(value, str) else len(value)
        if len(key) > MAX_KEY or  value_len > MAX_VALUE:
            raise Exception
        if cmd == 'add' and key in self._cache:
            return False
        if cmd == 'replace' and key not in self._cache:
            return False
        creat_time = vals[1]
        expire = time + create_time if time > 0 else 0
        self._cache[key] = (value, expire)
        return True            
            
    def _get(self, cmd, key, delta = None):
        if len(key) > MAX_KEY or (delta is not None and not isinstance(delta, int)):
            raise Exception
        if key not in self._cache:
            return None
        value = self._cache[key]
        flag = False
        if value[1] > 0 and t.time() > value[1]:
            self._cache.pop(key)
            return None
        ret = value[0]
        if self.countable(ret):
            flag = True
            if long(ret) > MAX_INT:
                ret = MAX_INT
            if long(ret) < MIN_INT:
                ret = MIN_INT
        if cmd == 'get':
            return ret
        if cmd == 'incr':
            if not flag:
                return str(delta)
            incr = int(ret) + delta    
            if incr > MAX_INT:
                return str(MIN_INT + delta - (MAX_INT - int(ret)) - 1) 
            if incr < MIN_INT:
                return str(MAX_INT + delta - (int(ret) - MIN_INT) + 1)
            return str(incr)
        if cmd == 'decr':
            if not flag:
                return '0'
            decr = int(ret) - delta
            if decr < MIN_INT:
                return str(MAX_INT - delta + (int(ret) - MIN_INT) + 1)
            if decr > MAX_INT:
                return str(MIN_INT - delta + (MAX_INT - int(ret)) - 1)
            if decr < 0:
                return '0'
            return str(decr)
        
    def set(self, key, value, time = 0, min_compress_len = 0):
        return self._set('set', key, (value, t.time()), time)
    
    def add(self, key, value, time = 0, min_compress_len = 0):            
        return self._set('add', key, (value, t.time()), time)

    def replace(self, key, value, time = 0, min_compress_len = 0):
        return self._set('replace', key, (value, t.time()), time)

    def get(self, key):
        return self._get('get', key)
    
    def incr(self, key, delta = 1):  
        return self._get('incr', key, delta)

    def decr(self, key, delta = 1):
        return self._get('decr', key, delta)

    def delete(self, key, time = 0):
        if key not in self._cache:
            return False
        if time > 0:
            self._cache[key][1] = t.time() + time
        else:
            self._cache.pop(key)

    def set_multi(self, mapping, time = 0, key_prefix = None, min_compress_len = 0):
        if len(mapping) > MAX_MULTI:
            raise Exception 
        creat_time = t.time()
        ret = []
        for k, v in mapping.items():
            _k = k if key_prefix is None else key_prefix + k
            if self._set('set', _k, (v, creat_time), time) == False:
                ret.append(k)
        return ret

    def get_multi(self, keys, key_prefix = None):
        if len(keys) > MAX_MULTI:
            raise Exception 
        values = []
        for k in keys:
            if key_prefix is not None:
                k = key_prefix + k
            values.append(self._get('get', k))
        return dict(zip(keys, values))                   
            
                        
