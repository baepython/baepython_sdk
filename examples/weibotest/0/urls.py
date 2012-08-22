# -*- coding: utf-8 -*-

__author__ = 'Michael Liao'

import json
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
import urllib2
import hashlib
import logging

import web

from weibo import APIClient

from framework import handler
from framework import odict
from framework import cache
from framework import db

try:
    from configdemo import APP_KEY, APP_SECRET
except ImportError:
    from config import APP_KEY, APP_SECRET

_CALLBACK_URL = 'http://weibotest.duapp.com/callback'

_DAYS = [u'星期一', u'星期二', u'星期三', u'星期四', u'星期五', u'星期六', u'星期日']

_DEFAULT_CITY = u'2151330'

# key: english name, value: [yahoo weather code, chinese name, weibo picture name]

_WEATHER_CODES = {
        u'tornado'              : [0, u'龙卷风', u'[龙卷风]'],
        u'tropical storm'       : [1, u'热带风暴', u''],
        u'hurricane'            : [2, u'飓风', u''],
        u'severe thunderstorms' : [3, u'风暴', u''],
        u'thunderstorms'        : [4, u'雷雨', u'[闪电]'],
        u'mixed rain and snow'  : [5, u'雨夹雪', u'[雪]'],
        u'mixed rain and sleet' : [6, u'雨夹冰雹', u'[冰雹]'],
        u'mixed snow and sleet' : [7, u'雪夹冰雹', u'[冰雹]'],
        u'freezing drizzle'     : [8, u'冰毛毛雨', u'[下雨]'],
        u'drizzle'              : [9, u'毛毛雨', u'[下雨]'],
        u'freezing rain'        : [10, u'冰雨', u'[下雨]'],

        u'showers'            : [11, u'阵雨', u'[下雨]'],
        u'showers'            : [12, u'阵雨', u'[下雨]'],
        u'snow flurries'      : [13, u'小雪', u'[雪]'],
        u'light snow showers' : [14, u'小雨雪', u'[雪]'],
        u'blowing snow'       : [15, u'风雪', u'[雪]'],
        u'snow'               : [16, u'下雪', u'[雪]'],
        u'hail'               : [17, u'冰雹', u'[冰雹]'],
        u'sleet'              : [18, u'雨夹雪', u'[雪]'],
        u'dust'               : [19, u'尘土', u'[沙尘暴]'],
        u'foggy'              : [20, u'雾', u'[雾]'],

        u'haze'                  : [21, u'霾', u'[雾]'],
        u'smoky'                 : [22, u'烟雾', u'[雾]'],
        u'blustery'              : [23, u'狂风', u'[风]'],
        u'windy'                 : [24, u'大风', u'[风]'],
        u'cold'                  : [25, u'寒冷', u''],
        u'cloudy'                : [26, u'多云', u'[阴天]'],
        u'mostly cloudy (night)' : [27, u'多云', u'[阴天]'],
        u'mostly cloudy (day)'   : [28, u'多云', u'[阴天]'],
        u'mostly cloudy'         : [28, u'多云', u'[阴天]'],
        u'partly cloudy (night)' : [29, u'局部多云', u'[阴天]'],
        u'partly cloudy (day)'   : [30, u'局部多云', u'[阴天]'],
        u'partly cloudy'         : [30, u'局部多云', u'[阴天]'],

        u'clear (night)'           : [31, u'晴朗', u'[阳光]'],
        u'clear'                   : [31, u'晴朗', u'[阳光]'],
        u'sunny'                   : [32, u'晴', u'[阳光]'],
        u'fair (night)'            : [33, u'晴朗', u'[阳光]'],
        u'fair (day)'              : [34, u'晴朗', u'[阳光]'],
        u'fair'                    : [34, u'晴朗', u'[阳光]'],
        u'mixed rain and hail'     : [35, u'雨夹冰雹', u'[冰雹]'],
        u'hot'                     : [36, u'炎热', u'[阳光]'],
        u'isolated thunderstorms'  : [37, u'局部雷雨', u'[闪电]'],
        u'scattered thunderstorms' : [38, u'零星雷雨', u'[闪电]'],
        u'scattered thunderstorms' : [39, u'零星雷雨', u'[闪电]'],
        u'scattered showers'       : [40, u'零星阵雨', u'[下雨]'],

        u'heavy snow'              : [41, u'大雪', u'[雪]'],
        u'scattered snow showers'  : [42, u'零星雨夹雪', '[雪]'],
        u'heavy snow'              : [43, u'大雪', u'[雪]'],
        # u'partly cloudy'           : [44, u'局部多云', u''],
        u'thundershowers'          : [45, u'雷阵雨', u'[闪电]'],
        u'snow showers'            : [46, u'小雪', u'[雪]'],
        u'isolated thundershowers' : [47, u'局部雷雨', u'[闪电]'],

        u'not available' : [3200, u'暂无数据', u'']
}

def _get_day(d):
    return [u'%s-%s-%s' % (d.year, d.month, d.day), _DAYS[d.weekday()]]

def _get_today():
    return _get_day(date.today())

def _get_tomorrow():
    return _get_day(date.today() + timedelta(days=1))

def _get_cities():
    L = list(db.select('city', order='alias'))
    city_list = []
    w_dict = dict()
    y_dict = dict()
    for c in L:
        oc = odict(name=c.name, alias=c.alias, yahoo_code=c.yahoo_code, weibo_code=c.weibo_code)
        city_list.append(oc)
        w_dict[oc.weibo_code] = oc.yahoo_code
        y_dict[oc.yahoo_code] = oc.weibo_code
    return (city_list, w_dict, y_dict)

def _make_cookie(uid, access_token):
    s = u'%s:%s' % (uid, access_token)
    return '%s:%s' % (uid, hashlib.md5(str(s)).hexdigest())

def _extract_cookie(cookie_str):
    if cookie_str:
        ss = cookie_str.split(u':')
        if len(ss)==2:
            return ss[0], ss[1]
    return None, None

def _get_user_from_cookie():
    uid, hash = _extract_cookie(web.cookies().get('weibouser'))
    if not uid:
        logging.info('no cookie found.')
        return None
    users = list(db.select('user', where='uid=$uid', vars=dict(uid=uid)))
    if not users:
        logging.info('no such user: %s' % uid)
        return None
    u = users[0]
    if hashlib.md5(str(u'%s:%s' % (uid, u.access_token))).hexdigest()!=hash:
        logging.info('user found, but hash not match.')
        return None
    return u

@handler('GET')
def index():
    user = _get_user_from_cookie()
    city = web.input().get('city', None)
    logging.info('get city from url: %s' % city)
    cities, wdict, ydict = _get_cities()
    if city not in ydict:
        city = None
        logging.info('invalid city from url.')
    if user and not city:
        # guess city:
        pcode = u'001%03d' % int(user.province_code)
        ycode = wdict.get(pcode, None)
        if not ycode:
            pcode = u'001%03d%03d' % (int(user.province_code), int(user.city_code))
            ycode = wdict.get(pcode, None)
        if ycode:
            city = ycode
            logging.info('locate user to city: %s' % city)
    if not city:
        city = _DEFAULT_CITY
        logging.info('set to default city.')
    return dict(user=user, city=city, cities=cities, today=_get_today(), tomorrow=_get_tomorrow())

@handler('GET')
def login():
    client = APIClient(app_key=APP_KEY, app_secret=APP_SECRET)
    raise web.found(client.get_authorize_url(_CALLBACK_URL))

@handler('GET')
def logout():
    web.setcookie('weibouser', 'x', expires=-1)
    raise web.found('/index')

@handler('GET')
def callback():
    i = web.input()
    code = i.get('code', None)
    if code:
        # /callback?code=xxx
        client = APIClient(app_key=APP_KEY, app_secret=APP_SECRET)
        token = client.request_access_token(code, _CALLBACK_URL)
        logging.info('got access token: %s' % str(token))
        uid = token.uid
        kw = dict(access_token=token.access_token, expires_in=token.expires_in)
        # check for update:
        if 0==db.update('user', where='uid=$uid', vars=dict(uid=uid), **kw):
            # create user:
            client.set_access_token(token.access_token, token.expires_in)
            user = client.get.users__show(uid=uid)
            kw['uid'] = uid
            kw['name'] = user.screen_name
            kw['gender'] = user.gender
            kw['province_code'] = user.province
            kw['city_code'] = user.city
            kw['image_url'] = user.profile_image_url
            db.insert('user', **kw)
        # make a cookie:
        web.setcookie('weibouser', _make_cookie(uid, token.access_token), int(token.expires_in - time.time()))
        raise web.found('/index')

def _get_weather_code(eng_code):
    key = eng_code.lower()
    while True:
        value = _WEATHER_CODES.get(key, None)
        if value:
            return value
        if key.startswith(u'mostly '):
            key = key[7:]
        elif key.startswith(u'pm '):
            key = key[3:]
        else:
            return [3200, eng_code, u'']

def _get_weather(city):
    if not city:
        return r'{"code":"500","Message":"Missing Input: city"}'
    data = cache.get('city-%s' % city)
    if data:
        logging.info('got data from cache')
        web.header('X-Cache', 'Hit from cache')
        return data
    # check city:
    cities = list(db.select('city', where='yahoo_code=$code', vars=dict(code=city)))
    if not cities:
        return r'{"code":"500","Message":"Invalid Input: city"}'
    c = cities[0]
    w = c.yahoo_code
    logging.info('fetch from yahoo weather...')
    url = 'http://weather.yahooapis.com/forecastjson?w=%s&u=c' % w
    resp = urllib2.urlopen(url)
    if resp.code==200:
        logging.info('begin fetch...')
        data = json.loads(resp.read())
        data['city'] = c.name
        cond = data['forecast'][0]['condition']
        codes = _get_weather_code(cond)
        data['forecast'][0]['code'] = codes[0]
        data['forecast'][0]['condition'] = codes[1]
        data['forecast'][0]['image'] = codes[2]
        cond = data['forecast'][1]['condition']
        codes = _get_weather_code(cond)
        data['forecast'][1]['code'] = codes[0]
        data['forecast'][1]['condition'] = codes[1]
        data['forecast'][1]['image'] = codes[2]
        # cache it, but first calculate expires time:
        now = datetime.now()
        t = datetime(now.year, now.month, now.day)
        delta = now - t
        exp = 86400 - delta.seconds # makes it expires in midnight (24:00)
        if exp > 3600:
            exp = 3600
        logging.info('fetched and cache for %d seconds.' % exp)
        json_data = json.dumps(data)
        cache.set('city-%s' % city, json_data, exp)
        web.header('X-Cache', 'Miss from cache')
        return json_data
    return None

@handler('GET', False)
def weather():
    i = web.input()
    web.header('Content-Type', 'application/json')
    city = str(i.get('city', ''))
    data = _get_weather(city)
    if not data:
        logging.info('fetch failed.')
        return r'{"code":"500","Message":"Fetch failed"}'
    return data

@handler('GET', False)
def share():
    user = _get_user_from_cookie()
    if not user:
        return ur'出错啦！'
    i = web.input()
    city = str(i.get('city', ''))
    data = _get_weather(city)
    if not data:
        return ur'出错啦！'
    client = APIClient(app_key=APP_KEY, app_secret=APP_SECRET)
    client.set_access_token(user.access_token, user.expires_in)
    obj_data = json.loads(data)
    fcast = obj_data['forecast'][0]
    s = u'%s %s今日%s%s，%d ~ %d度。来自城市天气预报 http://t.cn/SxvH12' % (_get_today()[0], obj_data['city'], fcast['condition'], fcast['image'], int(fcast['low_temperature']), int(fcast['high_temperature']))
    client.post.statuses__update(status=s)
    return u'''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <title>城市天气预报分享成功！</title>
    <script type="text/javascript">
      function jump() { location.assign('http://weibo.com/u/%s'); }
      setTimeout('jump()', 3000);
    </script>
</head>
<body>
    <p>分享成功！3秒后跳转至您的微博首页！<a href="javascript:void(0)" onclick="jump()">立刻跳转</a></p>
</body>
</html>
''' % user.uid

#@handler('GET')
def list_city():
    cities = list(db.select('city'))
    return dict(cities=cities)

#@handler('POST')
def add_city():
    i = web.input()
    db.insert('city', name=i.name, alias=i.alias, yahoo_code=i.yahoo_code, weibo_code=i.weibo_code)
    raise web.found('/list_city')