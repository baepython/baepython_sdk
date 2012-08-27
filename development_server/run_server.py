#!/usr/bin/env python

import os
import imp
from werkzeug.serving import run_simple
from optparse import OptionParser

def main():
    parser = OptionParser()
    parser.add_option("-p", "--port", type="int", dest="port", default="8080",
                      help="port")
    parser.add_option("--app", type="str", dest="app_root", default='demo/',
		              help="app_root")
    options, args = parser.parse_args()

    app_root = os.path.abspath(os.path.expanduser(options.app_root))
    if not os.path.isdir(app_root):
        print "Invaild app_root"    	
        return
    os.environ['APP_ROOT'] = app_root
    
    try:
        index = imp.load_source('index', os.path.join(app_root, 'index.py'))
    except IOError:
        print "Can't find index.py"
        return

    if not hasattr(index, 'application'):
        print "Can't find application"
        return

    if not callable(index.application):
        print "Invaild application"
        return

    files = ['index.py']

    try:
        run_simple('localhost', options.port, index.application,
                    use_reloader = True,
                    use_debugger = True,
                    extra_files = files,
                    threaded=True)
    except KeyboardInterrupt:
        pass 

if __name__ == '__main__':
    main()
