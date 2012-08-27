import os
import copy
import time as t
import pickle
try:
    import simplejson as json
except:
    import json

RETURN = {u'request_id' : 0}

class BaeTaskQueueManager(object):
    @staticmethod
    def getInstance(*args):
        return BaeTaskQueueManager(*args)
    
    def __init__(self, *args):
        self._cache = {} #{qname, Queue}
  
    def __del__(self):
        with open(os.path.join(os.environ['APP_ROOT'], 'taskqueuemgr.data.'+t.strftime("%Y%m%d%H%M%S")), 'w+') as f:
            pickle.dump(self._cache, f)
    
    def create(self, queue_name, queue_type, **kwargs):
        if queue_name in self._cache:
            raise Exception
        items = {'type': queue_type}
        items.update(kwargs)
        ins = BaeTaskQueue(queue_name, **items)
        self._cache[queue_name] = ins 
        return ins        
    
    def modify(self, queue_name, **kwargs):
        if queue_name not in self._cache:
            raise Exception
        if 'concurrency' in kwargs:
            self._cache[queue_name]._con = kwargs['concurrency']
        if 'max_length' in kwargs:
            self._cache[queue_name]._ml = kwargs['max_length']        
        return copy.deepcopy(RETURN)

    def getList(self):
        ret = copy.deepcopy(RETURN)
        if len(self._cache) == 0:
            return ret
        queues = []
        for k, v in self._cache.items():
            d = {u'timeout': v._to, 
                 u'show_name': v._name, 
                 u'default_callback_url': v._cb, 
                 u'retry_times': v._rt, 
                 u'queue_type': v._type, 
                 u'max_length': v._ml,
                 u'concurrency': v._con}
            queues.append(d)
        ret.update({u'response_params': {u'queues': queues}})
        return ret

    def remove(self, queue_name):
        if queue_name not in self._cache:
            raise Exception
        self._cache[queue_name]._removed = True
        self._cache.pop(queue_name)
        return copy.deepcopy(RETURN)

def decorator(func):
    def wrap(*args, **kwargs):
        if getattr(args[0], '_removed'):
            raise Exception
        return func(*args, **kwargs)
    return wrap

class BaeTaskQueue(object):
    def __init__(self, queue_name, **kwargs):
        self._name = unicode(queue_name)
        self._type = unicode(kwargs['type'])
        self._cb = unicode(kwargs.get('default_callback_url', ''))
        self._con = unicode(kwargs.get('concurrency', '1'))
        self._rt = unicode(kwargs.get('retry_times', '0'))
        self._ml = unicode(kwargs.get('max_length', '1000' if self._type == 1 else '10'))
        self._to = unicode(kwargs.get('timeout', '30' if self._type == 1 else '36000'))
        
        self._tasks = []
        self._removed = False

    def __del__(self):
        with open(os.path.join(os.environ['APP_ROOT'], 'taskqueue.data.'+t.strftime("%Y%m%d%H%M%S")), 'w+') as f:
            pickle.dump(self._tasks, f)
    
    @decorator
    def getTaskInfo(self, task_id):
        if task_id >= len(self._tasks):
            raise Exception
        ret = copy.deepcopy(RETURN)
        params = {u'response_params': {u'task_type': self._type, 
                                       u'task_id': task_id, 
                                       u'callback_url': self._cb, 
                                       u'app_id': u'0', 
                                       u'retry_max_times': self._rt, 
                                       u'timeout': self._to, 
                                       u'task_status': u'2',
                                       u'task_desc': unicode(json.dumps(self._tasks[task_id]))}}
        ret.update(params)
        return ret   

    @decorator
    def push(self, **kwargs):
        if 'url' in kwargs:
            kwargs['method'] = 'post' if 'params' in kwargs else 'get'
        self._tasks.append(kwargs)
        ret = copy.deepcopy(RETURN)
        ret.update({u'response_params': {u'task_id': len(self._tasks) - 1}}) 
        return ret      

    @decorator
    def query(self):
        ret = copy.deepcopy(RETURN)
        params = {u'response_params': {u'concurrency': self._con, 
                                       u'show_name': self._name,  
                                       u'default_callback_url': self._cb, 
                                       u'retry_times': self._rt, 
                                       u'queue_type': self._type, 
                                       u'max_length': self._ml, 
                                       u'timeout': self._to, 
                                       u'task_num': unicode(len(self._tasks))}}
        ret.update(params)
        return ret
                     
