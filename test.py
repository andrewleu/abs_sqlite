# -*- coding: utf-8 -*-
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

urls= (
 "/", "index",
)

if __name__ == "__main__":
    app = web.application(urls, globals())
    try:
      app.run()
    except KeyboardInterrupt :
      print "exitting"
    finally :
      exit(0)


count=0
class index:
    def GET(self):
        global count
        count += 1; cnt=str(count); a=('Refreshing', cnt, 'aabbccdd')
        return  self.refresh_page(a)
    def refresh_page(self,*a):
       global ses_cur
       yield '<!Doctype html> <html xmlns=http://www.w3.org/1999/xhtml> \
         <head> \
         <meta http-equiv=Content-Type content="text/html;charset=utf-8">\
         </head> <body> <h1>'
       yield a[0]+ ' ' +a[1] +'</h1>'
       yield  '<script language="JavaScript">function myrefresh(){   window.location.reload();}'
       yield  "setTimeout('myrefresh()',2000); \
          </script> </body>\
          </html>"