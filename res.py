# -*- coding: utf-8 -*-

import time
import telnetlib
import sqlite3
import web
import abs_bd_sqlite
import os
from web import form
render=abs_bd_sqlite.render
class res(object):
  def __init__(self):
      """
        dbs = abs_bd_sqlite.return_db()
        c = sqlite3.connect(":memory:", check_same_thread=False)
        s = sqlite3.connect(":memory:", check_same_thread=False)
        a = c;
        b = s
        c = dbs[0];
        s = dbs[1];
        a.close();
        b.close()
        """
      self.cur_tab = abs_bd_sqlite.cur_tab;# print "cur-tab:"+ str(self.cur_tab)
      self.ses_cur = abs_bd_sqlite.ses_cur;# print "ses-cur:"+ str(self.ses_cur)
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
        BUF = 65535
        # print query
        name = name.split("&")
        cookie = web.cookies().get('webpy_session_id');
        print "cookie:", cookie  # get the cookie
        timestamp = long(time.time())
        self.ses_cur.execute("select count from session where cookie='%s' and encryptstr='%s'" % (cookie,name[1]))
        q = self.ses_cur.fetchone(); 
        if q is None:  # new cookie
            self.ses_cur.execute("insert into session(cookie, timestamp,encryptstr) values('%s',%d,'%s')" % (cookie, timestamp,name[1]))
            count = 0
        else :
            count=q[0]
        self.ses_cur.execute("select * from session");
        print 'in the database:\n'+str(self.ses_cur.fetchall())
        print name
        if len(name) == 2:  # check the data base for the file
            query = 1
            self.cur_tab.execute(
                "select filename,mediatype,bandwith from filelist where rand='%s' and encryptstr='%s'" % (
                    name[0], name[1]))
            result = self.cur_tab.fetchone();
            print result
        else:
            query = 0

        if query != 0:
            print 'count:',count
            information = {
                0:  [ u"传送标签",name[0] + "&" + name[1]],
                1:  [u"确定文件",result[0]],
                2:  [u"设定带宽",result[2]],
                3:  [u"开始播放", ''],
                4:  ["",""]
                } [count%5]
            print information;
            count +=1
            self.ses_cur.execute("update session set count=%d where cookie='%s' and encryptstr='%s'" % (count, cookie,name[1]))
            # update the session
            # to display the video does not need yielding the following
            if count%5 != 0:
                yield '<!Doctype html> <html xmlns=http://www.w3.org/1999/xhtml> \
                <head> \
                <meta http-equiv=Content-Type content="text/html;charset=utf-8">\
                </head> <body> <h1>'
                yield information[0] + '</h1> <p>'
                yield information[1]
                yield '</p><script language="JavaScript">function myrefresh(){   window.location.reload();}'
                yield "setTimeout('myrefresh()',2000); \
                 </script> </body> </html>"
            #self.refreshpage(information)
        if query != 0 and count%5==0:
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
          if count%5 == 0 : 
            # cur_tab.execute("commit")
            f = abs_bd_sqlite.okform()
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
web.config.debug = False
if __name__ == "__main__":
    app = web.application(urls, globals())
    session = web.session.Session(app, web.session.DiskStore('webpy.sessions'), initializer={'count': 0})
    try:
        app.run()
    except KeyboardInterrupt:
        tabl.close()
        print "exitting"
    finally:
        exit(0)
