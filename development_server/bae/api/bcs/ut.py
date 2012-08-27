# -*- coding: utf-8 -*-
import os
import time
from bcs import BaeBCS

BCS_HOST   = "http://bcs.duapp.com"
ACCESS_KEY = "your access key" 
SECRET_KEY = "your secret key"

def test():
    bcs = BaeBCS(BCS_HOST, ACCESS_KEY, SECRET_KEY)
    bname = "your_bucket"

    filename = os.path.dirname(__file__) + "/testdata" 
    with open(filename) as fd:
        data = fd.read()

    print "list_buckets()"
    e, d = bcs.list_buckets()
    assert e == 0
    print d

    print "get_acl()"
    e, d = bcs.get_acl(bname, '')
    assert e == 0
    print d

    obj1 = "/obj1"
    obj2 = "/obj2"
    obj3 = "/obj3"
    sup1 = "/sup1"

    print "put_object()"
    e, d = bcs.put_object(bname, obj1, data)
    assert e == 0
    time.sleep(1)

    print "get_object()"
    e, d = bcs.get_object(bname, obj1)
    assert e == 0
    #assert d == data

    print "get_acl()"
    e, d = bcs.get_acl(bname, obj1)
    assert e == 0
    print d

    print "make_public()"
    e, d = bcs.make_public(bname, obj1, "chenyf")
    assert e == 0

    print "get_acl()"
    e, d = bcs.get_acl(bname, obj1)
    assert e == 0
    print d

    print "list_objects()"
    e, d = bcs.list_objects(bname)
    assert e == 0
    print d

    print "copy_object()"
    e, d = bcs.copy_object(bname, obj1, bname, obj2)
    assert e == 0
    time.sleep(1)

    print "put_superfile()"
    objlist = [(bname, obj1), (bname, obj2)]
    e, d = bcs.put_superfile(bname, sup1, objlist )
    print e
    print d
    #assert e == 0
    time.sleep(1)

    print "put_file()"
    e, d = bcs.put_file(bname, obj3, filename)
    assert e == 0
    time.sleep(1)

    filename2 = os.path.dirname(__file__) + "/testdata2" 
    os.system("rm -f %s" % filename2)

    print "get_to_file()"
    e, d = bcs.get_to_file(bname, obj3, filename2)
    assert e == 0

    print "del_object()"
    e, d = bcs.del_object(bname, obj1)
    assert e == 0
    time.sleep(1)

    print "get_object()"
    e, d = bcs.get_object(bname, obj1)
    assert e != 0
    print e
 
    obj4 = "/dir1/obj4"
    print "put_object()"
    e, d = bcs.put_object(bname, obj2, data)
    assert e == 0
    time.sleep(1)

    print "get_object"
    e, d = bcs.get_object(bname, obj2)
    assert e == 0
    assert d == data

if __name__ == "__main__":
    test()
     
    
