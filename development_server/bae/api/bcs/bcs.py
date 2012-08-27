# -*- coding: utf-8 -*-

import hmac, base64, hashlib
import json
import os
import urllib

try:
    from bae.api import logging
except:
    import logging

from httpc import HttplibHTTPC

ERR_OK       = 0
ERR_RESPONSE = -1

class BaeBCS(object):
    def __init__(self, host=None, ak=None, sk=None, httpclient_class=None):
        """构造函数
        参数
            host(str):       BCS服务器地址
            ak(str):         access key
            sk(str):         secret key
            httpclient_class:  与BCS服务器交互的HTTP接口类，默认为HttplibHTTPC
        """
        self.host = host
        self.ak   = ak
        self.sk   = sk
        if self.host.endswith('/') :
            self.host = host[:-1]
        if not self.host.startswith('http'):
            self.host = "http://" + self.host
        hc_class = (httpclient_class if httpclient_class else HttplibHTTPC)
        self.httpc = hc_class()
        self.get_url = self._sign('GET', '', '/')

    def list_buckets(self):
        """列举属于自己的buckets
        参数：
        返回值：
            返回值为 (errcode, response)形式的tuple
            其中errcode为错误码，ERR_OK表示成功，其它表示失败
            成功情况下，response为bucket name列表
            失败情况下，response是服务器返回的原始信息
        异常：
            httplib.HTTPException:  同后端交互过程中出现网络错误
        """
        r = self.httpc.get(self.get_url)
        e, d = self._handle_response(r, 2)
        if e != ERR_OK:
            return (e, d)
        return (e, [b['bucket_name'].encode('utf8') for b in d])

    def put_object(self, bname, oname, data):
        """上传数据到指定object
        参数：
            bname(str):     bucket name，必须预先创建
            oname(str):     object name
            data：          待上传的数据
        返回值：
            返回值为 (errcode, response)形式的tuple
            其中errcode为错误码，ERR_OK表示成功，其它表示失败
            成功情况下，response为None
            失败情况下，response是服务器返回的原始信息
        异常：
            httplib.HTTPException:  同后端交互过程中出现网络错误
        """
        url = self._sign('PUT', bname, oname)
        r = self.httpc.put(url, data, headers={})
        return self._handle_response(r)
 
    def get_object(self, bname, oname):
        """下载object
        参数：
            bname(str):     bucket name，必须预先创建
            oname(str):     object name
        返回值：
            返回值为 (errcode, response)形式的tuple
            其中errcode为错误码，ERR_OK表示成功，其它表示失败
            成功情况下，response为object对应的数据
            失败情况下，response为服务器返回的原始信息
        异常：
            httplib.HTTPException:  同后端交互过程中出现网络错误
        """
        url = self._sign('GET', bname, oname)
        r = self.httpc.get(url, headers={})
        return self._handle_response(r, 1)

    def del_object(self, bname, oname):        
        """删除object
        参数：
            bname(str):     bucket name，必须预先创建
            oname(str):     object name
        返回值：
            返回值为 (errcode, response)形式的tuple
            其中errcode为错误码，ERR_OK表示成功，其它表示失败
            成功情况下，response为None
            失败情况下，response是服务器返回的原始信息
        异常：
            httplib.HTTPException:  同后端交互过程中出现网络错误
        """
        url = self._sign('DELETE', bname, oname)
        r = self.httpc.delete(url, headers={})
        return self._handle_response(r)

    def list_objects(self, bname, prefix='', start=0, limit=100):
        """列举指定bucket下的所有object
        参数：
            bname(str):     bucket name，必须预先创建
            prefix(str)：   若指定，则只返回符合prefix的object
            start(int):     list起始下标，默认为0
            limit(int):     返回结果集个数，默认为100
        返回值：
            返回值为 (errcode, response)形式的tuple
            其中errcode为错误码，ERR_OK表示成功，其它表示失败
            成功情况下，response为object name列表
            失败情况下，response为服务器返回的原始信息
        异常：
            httplib.HTTPException:  同后端交互过程中出现网络错误
        """
        params = { 'start': start, 'limit': limit}
        if prefix:
            params.update ({'prefix': prefix})
        url = self._sign('GET', bname, '/') + '&' + urllib.urlencode(params)
        r = self.httpc.get(url)
        e, d = self._handle_response(r, 2)
        if e != ERR_OK:
            return (e, d)
        return (e, [o['object'].encode('utf-8') for o in d['object_list'] ]) 

    def copy_object(self, src_bname, src_oname, dst_bname, dst_oname):
        """ 复制object
        参数：
            src_bname(str):     源bucket name
            src_oname(str):     源object name
            dst_bname(str):     目的bucket name
            dst_oname(str):     目的object name
        返回值：
            返回值为 (errcode, response)形式的tuple
            其中errcode为错误码，ERR_OK表示成功，其它表示失败
            成功情况下，response为None
            失败情况下，response是服务器返回的原始信息
        异常：
            httplib.HTTPException:  同后端交互过程中出现网络错误
        """
        headers = {}
        headers.update( {
                'x-bs-copy-source': "bs://%s%s" % (src_bname, src_oname),
                'x-bs-copy-source-directive': 'copy', # copy or replace
                })
        url = self._sign('PUT', dst_bname, dst_oname)
        r = self.httpc.put(url, '', headers)
        return self._handle_response(r)

    def put_superfile(self, bname, oname, objlist):
        """上传superfile
        参数：
            bname(str):     bucket name，必须预先创建
            oname(str):     object name
            objlist(list)： 组成superfile的object列表，形式为 [('bucket1', '/obj1'), ('bucket2', '/obj2')]          
        返回值：
            返回值为 (errcode, response)形式的tuple
            其中errcode为错误码，ERR_OK表示成功，其它表示失败
            成功情况下，response为None
            失败情况下，response是服务器返回的原始信息
        异常：
            httplib.HTTPException:  同后端交互过程中出现网络错误
        """
        l = []
        try:
            for idx, (b, o) in enumerate(objlist):
                r = self._head_object(b, o)
                etag = r['header']['etag']
                l.append('"part_%d": {"url": "bs://%s%s", "etag":"%s"}' % (
                    idx, b, o, etag))
        except Exception, e:
            return (ERR_RESPONSE, str(e))

        meta = '{"object_list": {%s}}' % (  ','.join(l)  )
        url = self._sign('PUT', bname, oname) + '&superfile=1'
        r = self.httpc.put(url, meta, headers={})
        return self._handle_response(r)

    def set_acl(self, bname, oname, acl):
        """ 设置bucket或者object的ACL
        参数：
            bname(str):     bucket name，必须预先创建
            oname(str):     object name；若为''，表示设置bucket的ACL，否则设置object的ACL
            acl(str)：      描述指定bucket或object的ACL的字符串
        返回值：
            返回值为 (errcode, response)形式的tuple
            其中errcode为错误码，ERR_OK表示成功，其它表示失败
            成功情况下，response为None
            失败情况下，response是服务器返回的原始信息
        异常：
            httplib.HTTPException:  同后端交互过程中出现网络错误
        """
        url = self._sign('PUT', bname, oname) + '&acl=1'
        r = self.httpc.put(url, acl, headers={})
        return self._handle_response(r)

    def get_acl(self, bname, oname):
        """ 获取bucket或者object的ACL
        参数：
            bname(str):     bucket name，必须预先创建
            oname(str):     object name；若为'',表示获取bucket的ACL，否则获取object的ACL
        返回值：
            返回值为 (errcode, response)形式的tuple
            其中errcode为错误码，ERR_OK表示成功，其它表示失败
            成功情况下，response为描述bucket或object对应的ACL的字符串
            失败情况下，response为服务器返回的原始信息
        异常：
            httplib.HTTPException:  同后端交互过程中出现网络错误
        """
        url = self._sign('GET', bname, oname) + '&acl=1'
        r = self.httpc.get(url, headers={})
        return self._handle_response(r, 1)

    def put_file(self, bname, oname, filename):
        """上传文件到指定的object
        参数：
            bname(str):     bucket name，必须预先创建
            oname(str):     object name
            filename(str)： 待上传的文件
        返回值：
            返回值为 (errcode, response)形式的tuple
            其中errcode为错误码，ERR_OK表示成功，其它表示失败
            成功情况下，response为None
            失败情况下，response是服务器返回的原始信息
        异常：
            httplib.HTTPException:  同后端交互过程中出现网络错误
        """
        if not os.path.isfile(filename):
            raise Exception(filename + ' is not a file')

        url = self._sign('PUT', bname, oname)
        r = self.httpc.put_file(url, filename, headers={})
        return self._handle_response(r)

    def get_to_file(self, bname, oname, filename):
        """ 下载指定object的数据，并保存到指定文件中
        参数：
            bname(str):     bucket name，必须预先创建
            oname(str):     object name
            filename(str)： 用于保存数据的文件
        返回值：
            返回值为 (errcode, response)形式的tuple
            其中errcode为错误码，ERR_OK表示成功，其它表示失败
            成功情况下，response为None
            失败情况下，response是服务器返回的原始信息
        异常：
            httplib.HTTPException:  同后端交互过程中出现网络错误
        """
        url = self._sign('GET', bname, oname)
        r = self.httpc.get_file(url, filename, headers={})
        return self._handle_response(r)

    def make_public(self, bname, oname, user=None):
        """ 允许指定user访问指定的bucket或object
        参数：
            bname(str):     bucket name，必须预先创建
            oname(str):     object name
            user(str)：     授权的用户名称，若不指定，则表示所有用户
        返回值：
            返回值为 (errcode, response)形式的tuple
            其中errcode为错误码，ERR_OK表示成功，其它表示失败
            成功情况下，response为None
            失败情况下，response是服务器返回的原始信息
        异常：
            httplib.HTTPException:  同后端交互过程中出现网络错误
        """
        acl = '{"statements":[{"action":["*"],"effect":"allow","resource":["%s%s"],"user":["%s"]}]}' % (
            bname, oname, (user if user else "*"))
        return self.set_acl(bname, oname, acl)


    ### internal functions        
    def _sign(self, M, B, O, T=None, I=None, S=None):
        flag = ''
        s =  ''
        if M :   flag+='M'; s += 'Method=%s\n' % M; 
        if B :   flag+='B'; s += 'Bucket=%s\n' % B; 
        if O :   flag+='O'; s += 'Object=%s\n' % O; 
        if T :   flag+='T'; s += 'Time=%s\n'   % T; 
        if I :   flag+='I'; s += 'Ip=%s\n'     % I; 
        if S :   flag+='S'; s += 'Size=%s\n'   % S; 

        s = '\n'.join([flag, s])
        
        def h(sk, body):
            digest = hmac.new(sk, body, hashlib.sha1).digest()
            t = base64.encodestring(digest)
            return urllib.quote(t.strip())

        sign = h(self.sk, s)
        url = '%s/%s%s?sign=%s:%s:%s' % (
                self.host, B, '/' + urllib.quote(O[1:]), 
                flag, self.ak, sign)
        if T :      url += '&time=%s'   % T;
        if I :      url += '&ip=%s'     % I; 
        if S :      url += '&size=%s'   % S; 
        return url

    def _head_object(self, bname, oname):
        url = self._sign('HEAD', bname, oname)
        return self.httpc.head(url, headers={})

    def _handle_response(self, r, body=0):
        if not isinstance(r, dict):
            return (ERR_RESPONSE, r)

        try:
            status = r['status']
            if status not in [200, 206]:
                j = json.loads(r['body'])
                return (int(j['Error']['code']), r)

            ### success
            if body == 0:
                return (ERR_OK, None)
            elif body == 1:
                return (ERR_OK, r['body'])
            else:
                return (ERR_OK, json.loads(r['body']))
        except Exception, e:
            logging.warning("_handle_response exception: %s" % str(e))
            return (ERR_RESPONSE, r)

