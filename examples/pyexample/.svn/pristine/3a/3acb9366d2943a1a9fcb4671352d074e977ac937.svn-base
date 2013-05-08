# -*- coding: utf-8 -*-

from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.shortcuts import render

#### 一个可以上传文件，并将文件保存到BCS中的示例

def index(request):
    return render(request, 'upload/index.html', {})


BCS_HOST="http://bcs.duapp.com"
def upload(request):

    ### 将用户上传的文件的数据保存到 data 中
    uf = request.FILES.get('file', None)
    data = uf.read()

    ### 获得上传文件的名称和大小
    name = uf.name
    size = uf.size

    ### 将文件保存到百度云存储 BCS 中


    from bae.api.bcs import BaeBCS
    bcs = BaeBCS(host=BCS_HOST)

    ### 你的bucket name， 请到BCS管理界面上去设置
    bname = "pyupload"

    ### object name， 可以随便设置；这里将文件的MD5作为文件名称
    ##oname = "/%s" % name.encode('utf8')
    import hashlib
    tt = hashlib.md5(data).hexdigest()
    a = name.encode('utf8').split('.')
    if len(a) > 1:
        oname = "/%s.%s" % (tt, a[-1])
    else:
        oname = "/%s" % (tt)

    ### 将文件保存到BCS中
    e, d = bcs.put_object(bname, oname, data)
    if e != 0:
        s = "put_object failed: " + str(d)
        return HttpResponse(s)

    ### 将BCS中的文件设置为public， 这样别人才能访问到
    e, d = bcs.make_public(bname, oname)
    if e != 0:
        s = "make_public failed: " + str(d)
        return HttpResponse(s)

    ### 计算出BCS中文件的访问URL
    access_url = "%s/%s/%s" % (BCS_HOST, bname, oname)
    return HttpResponse("file access URL is %s" % access_url)
    #return HttpResponseRedirect(access_url)

