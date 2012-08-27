BAE Python本地调试环境
======================

Overview
--------
Bae Python本地调试环境支持用户在本地启动一个web server来模拟Bae线上情景，进行代码调试。
在该环境中还包括了几个常用线上服务接口的模拟，用户可以在本地环境中直接使用线上服务的调用接口，能得到相同格式的返回值。
另外，还包括了一个帮助用户上传下载代码的脚本和一个下载打包第三方库的脚本，方便用户进行日常的开发工作。

DirectoryTree
-------------
|-- development_server (本地开发环境根目录)

    |-- run_server.py  (启动一个web server)
    
    |-- baetools       (上传下载Bae App脚本)

    |-- bundle.py      (第三方库下载打包脚本) 
    
    |-- demo           (Bae App示例)
        |-- ..
    
    |-- misc           (依赖库目录)
        |-- ..

    |-- bae
        |-- api        (服务模拟, 包括memcache、rank、counter、taskqueue服务接口,使用参见 http://pythondoc.duapp.com/ )
            |-- ..
        |-- core       (wsgi)
            |-- ..  
HowTo
-----
*web server启动*
::
    
    # -p 指定端口 -app 指定本地运行的app目录
    ~$ ./run_server.py -p ${YOUR_PORT} --app=${YOUR_APP_ROOT}

*下载Bae app目录到本地, 部署本地目录到Bae*
::

    ~$ ./baetools -h
    Usage:
        baetools COMMAND [ARGS...]
        baetools help [COMMAND]

    Options:
        -h, --help  show this help message and exit

    Commands:
        help (?)       give detailed help on a specific sub-command
        pull (pl)      Download the Bae app repository
        push (ps)      Push local source to Bae

    # pull子命令, 从Bae SVN中取出指定代码树 (password和username只需指定一次, 其后能被保存使用)
    # 下载后保存的目录中不带版本控制, 开发者可以使用自己熟悉的CVS进行管理开发
    ~$ ./baetools pull -h
    pull (pl): Download the Bae app repository

    Usage:
        baetools pull [ARGS...]

    Options:
            -h, --help          show this help message and exit
            --password=PASSWD   specify svn repo passwd
            --username=UNAME    specify svn repo username
            -p PATH, --path=PATH
                                specify local path
            -v VERSION, --version=VERSION
                                specify Bae app version
            -u URL, --url=URL   specify Bae app SVN
   
   # push子命令, 将本地目录直接部署到Bae环境中
   ~$ ./baetools push -h
   push (ps): Push local source to Bae

   Usage:
       baetools push [ARGS...]

   Options:
       -h, --help          show this help message and exit
       --password=PASSWD   specify svn repo passwd
       --username=UNAME    specify svn repo username
       -v VERSION, --version=VERSION
                           specify Bae app version
       -u URL, --url=URL   specify Bae app SVN
       -d DIR, --dir=DIR   specify local source directory
                                                       
*第三方库下载打包*
::

    # -z 指定是否压缩为zip包, 开发者使用该脚本可以处理未被预装的第三方依赖
    # 该脚本依赖pip, 希望开发者最好在virtualenv中使用
    # 创建了第三方依赖库目录后，只需增加搜索路径即可使用 (import sys sys.path.insert(0, 'bundle' or 'bundle.zip'))
    ~$ ./bundle.py [-z] pkg1 pkg2 ... pkgN

Demo
----
开发者直接使用run_server.py来运行demo, 再使用curl命令访问, 可以看到‘Welcome to Baidu Cloud!’
