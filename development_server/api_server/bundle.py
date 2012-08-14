#!/usr/bin/env python

import os
import sys
import pip.locations
import shutil
import optparse
import subprocess
import glob

BUNDLE_DIR = 'bundle'

ZIP_BUNDLE = BUNDLE_DIR + '.zip'

installed_pkgs = [
"setuptools-0.6c11"
"pip-1.0.2",
"BeautifulSoup-3.2.0",
"Imaging-1.1.7",
"MarkupSafe-0.15",
"pycrypto-2.4.1",
"PyYAML-3.10",
"South-0.7.3",
"Jinja2-2.6",
"Pygments-1.4",
"numpy-1.6.1",
"WebOb-1.1.1",
"pytz-2011n",
"Paste-1.7.5.1",
"werkzeug-0.8.2",
"SQLAlchemy-0.7.5",
"Markdown-2.1.0",
"webapp2-2.5.1",
"Flask-0.8",
"Genshi-0.6",
"web.py-0.36",
"tornado-2.1.1",
"MySQL-python-1.2.3",
"Django-1.4.1",
"Django-1.3.1",
"Django-1.2.7"
]

def main():

    def get_pkg_name(p):   
        info = os.path.join(p, 'PKG-INFO')
        if os.path.exists(info):
            with open(info, 'r') as f:
               f.readline()
               name = f.readline().rstrip()
               name = name.split(' ')[1].lower()
               return name
        return None 
    
    def get_pkg_toplevels(p):
        tl_txt = os.path.join(p, 'top_level.txt')
	if os.path.exists(tl_txt):
            with open(tl_txt, 'r') as f:
                toplevels = f.readlines()      
                return toplevels
        return []

    def copy_pkg(p): 
        if os.path.isdir(p):
            shutil.copytree(p, os.path.join(BUNDLE_DIR, os.path.basename(p)), ignore = shutil.ignore_patterns('*.pyc'))
        else:
            shutil.copy2(p + '.py', BUNDLE_DIR)

    parser = optparse.OptionParser(usage = 'usage: ./bundle.py [-z] pkg1 pkg2 ...')
    parser.add_option("-z", dest = "zipmode", action = 'store_true', default = False,
                      help="format a zip file")
    (options, args) = parser.parse_args()
    
    if len(args) < 1:
        print 'usage: ./bundle.py [-z] pkg1 pkg2 ...'
        sys.exit(0)   
    
    if os.path.exists(BUNDLE_DIR):
        shutil.rmtree(BUNDLE_DIR)
    os.mkdir(BUNDLE_DIR)
  
    args = map(lambda p: p.lower(), args) 
    toinstall = set(args)
    installed = map(lambda p: p.split('-', 1)[0].lower(), installed_pkgs)
    toinstall = toinstall - set(installed)
    if len(toinstall) == 0:
        print '[All packages are installed by BAE]'
        return 
    
    print '[Downloading...]'
    pkgs = ' '.join(toinstall)     
    pip_cmd = os.path.join(os.environ['VIRTUAL_ENV'], 'bin/pip') 
    
    child = subprocess.Popen("%s install %s"%(pip_cmd, pkgs), stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = True)
    if child.wait() != 0:
        print '\n'.join(child.communicate()).strip()
        return 
    print '[Installation complete]'

    with open(os.path.join(BUNDLE_DIR, 'pkgs.txt'), 'w') as f:
        f.write('\n'.join(toinstall))
    
    for d in glob.glob(os.path.join(pip.locations.site_packages, "*.egg*")):
        mp = pip.locations.site_packages
        if d.endswith('egg'):
            d = os.path.join(d, 'EGG-INFO')     
            mp = os.path.join(pip.locations.site_packages, 'EGG-INFO')

        name = get_pkg_name(d)
        if name in toinstall:
            tls = get_pkg_toplevels(d)
            for tl in tls:
                copy_pkg(os.path.join(mp, tl.rstrip()))

    if options.zipmode:
        child = subprocess.Popen("/usr/bin/zip -r %s %s"%(ZIP_BUNDLE, BUNDLE_DIR), stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = True) 
        if child.wait() != 0:
            print '\n'.join(child.communicate()).strip()
            return 
        shutil.rmtree(BUNDLE_DIR)
 
if __name__ == '__main__':
    main()
