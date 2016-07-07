import web
import os
import string
import base64
import sys
import random
from Crypto.Cipher import AES
import urllib, urllib2
import sqlite3
from datetime import datetime
import time
import telnetlib

from web import form

reload(sys)
sys.setdefaultencoding("utf8")
tel = ' '


def refresh_page(note, count, cookie, display_content):
    global ses_cur
    refresh = 0
    values = {0: display_content,
              1: "播放文件" + display_content[0] + "，需要带宽" + display_content[2],
              2: "设定带宽" + display_content,
              3: ""}
    # displayed content after the h1
    if count >= 4:
        count = 0
        refresh = 1
    else:
        extra_content = values[count]
        count += 1
    ses_cur.execute("update session set count=%d where cookie='%s'" % count, cookie)
    # update the session
    if refresh == 0:  # to display the video does not need yielding the following
        yield '<!Doctype html> <html xmlns=http://www.w3.org/1999/xhtml> \
         <head> \
         <meta http-equiv=Content-Type content="text/html;charset=utf-8">\
         </head> <body> <h1>'
        yield note + '</h1> <p>'
        yield extra_content
        yield '</p><script language="JavaScript">function myrefresh(){   window.location.reload();}'
        yield "setTimeout('myrefresh()',2000); \
          </script> </body> </html>"


def __init__(self):
    self.tel = telnetlib.Telnet('192.168.0.1', 23, 60)
    self.tel.set_debuglevel(2)
    self.tel.read_until('Password:');  # h3c switch
    self.tel.write('bstar' + '\n');  # password
    self.tel.read_until('>')
    self.tel.write('system' + '\n');  # configuration mode
    self.tel.read_until(']')
    self.tel.write('interface GigabitEthernet 1/0/25' + '\n')
    self.tel.read_until(']')
    self.tel.write('qos lr outbound cir 10240' + '\n');
    self.tel.read_until(']')
    self.tel.write('quit' + '\n');
    # self.tel.write('disp this'+'\n') #default bandwith is 1M
    # print self.tel.read_all()


def GET(self, name):
    global cur_tab
    global ses_cur
    BUF = 65535
    # print query
    name = name.split("&")
    cookie = web.cookies().get('webpy_session_id');  # get the cookie
    timestamp = long(time.time())
    ses_cur.execute("select count from session where cookie=‘%s'" % cookie)
    count = ses_cur.fetchone()
    if count is None:  # new cookie
        ses_cur.execute("insert into session(cookie, timestamp) values('%s',%d)" % cookie, timestamp)
        count = 0

    if len(name) == 2:  # check the data base for the file
        query = cur_tab.execute(
            "select filename,mediatype,bandwith from filelist where rand='%s' and encryptstr='%s'" % (
                name[0], name[1]))
        result = cur_tab.fetchone()
    else:
        query = 0
    if query != 0:
        try:
            {
                0: lambda: refresh_page('读取标记:', 0, cookie, name[0] + '&' + name[1]),
                1: lambda: refresh_page('解析标记:', 1, cookie, result),
                2: lambda: refresh_page('设定带宽:', 2, cookie, result[2]),
                3: lambda: refresh_page('开始播放:', 3, cookie, '')
            }[count]()
        except KeyError:
            refresh_page('读取标记: ', 0, cookie, name[0] + '&' + name[1] )

    if query != 0:
        bd = result[2];
        print bd
        if bd == '40M':
            self.tel.write('interface GigabitEthernet 1/0/25' + '\n')
            self.tel.read_until(']')
            self.tel.write('qos lr outbound cir 40960' + '\n');
            self.tel.read_until(']')
            self.tel.write('quit' + '\n');
        self.tel.close()
        filename = result[0]
        filepath = os.path.join('/opt', filename);
        print filepath;  # for windows,
        web.header('Content-Type', result[1])
        web.header('Transfer-Encoding', 'chunked')
        f = open(filepath, 'r');
        # cur_tab.execute("commit")
        # cur_tab.close()
        while True:
            c = f.read(BUF)
            if c:
                yield c
            else:
                break
        f.close();
        raise web.seeother("/")
    else:
        # cur_tab.execute("commit")
        f = okform()
        yield render.warning("Warning", "<p>URL parsing error.</p>", f)


def POST(self, path):
    raise web.seeother("/")


'''
urls= (
   "/res/(.+)", "res",
  )
tabl=open_database('abs.db3');
cur_tab=tabl.cursor()
sessiondb=open_database(':memory:')
ses_cur=sessiondb.cursor()
ses_cur.execute('Create  TABLE session ( \
  timestamp long, \
  count int(2) DEFAULT 0, \
  cookie varchar(32) PRIMARY KEY \
  ) ;')
'''
if __name__ == "__main__":
    app = web.application(urls, globals())
    try:
        app.run()
    except KeyboardInterrupt:
        tabl.close()
        print "exitting"
    finally:
        exit(0)
