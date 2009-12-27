'''
Created on 2009-12-23

@author: pjq
'''
#!/usr/bin/env python2.6
#coding=utf8
import web
import Cookie, urllib
import simplejson as json
 
from google.appengine.api import urlfetch
from setting import app
from google.appengine.ext import db
from google.appengine.api import users
 
 
print 'run'
renren_usr = 'pengjianqing@gmail.com'
renren_passwd = '校内密码'
twitter_usr = 'pengjianqing@gmail.com'
twitter_passwd = 'twitter密码'
 
cookie_buf = Cookie.SimpleCookie();
 
class LastTweetRecord(db.Model):
    id = db.StringProperty(multiline=True);
    date = db.DateTimeProperty(auto_now_add=True)
 
def make_cookie_header(cookie):
    ret = ''
    for v in cookie.values():
        ret += '%s=%s;' % (v.key, v.value)
    return ret
 
def get_tweets (usr, passwd):
    last_tweet_id = 0
    last_tweet_record = None
    last_tweet_records = db.GqlQuery('SELECT * FROM LastTweetRecord ORDER BY date DESC');
      
    last_tweet_id=last_tweet_records[0].id;
    print 'last_tweet_id=',last_tweet_id,"<br>"
    print 'last update at ',last_tweet_records[0].date,"<br>"
 
    new_timeline = []
    timeline_uri = 'http://%s:%s@twitter.com/statuses/user_timeline.json?count=100&amp;' % (usr, passwd)
    timeline = urllib.urlopen(timeline_uri).read(); 
    
    timeline = json.loads(timeline)
 
    if len(timeline) == 0:
        return []
    
    database=LastTweetRecord()
    database.id= str(timeline[0]['user']["statuses_count"])
    print 'new_tweet_id=',database.id,"<br>"
    database.put()
    statuses_count=0
    i=0
    for tweet in timeline:
        i=i+1
        if i==10:
            break;
        for v,k in tweet.items():
            if v=="user":
                statuses_count=k['statuses_count']
        if str(statuses_count)==str(last_tweet_id):
            break
        if int(statuses_count)<int(last_tweet_id):
            break
        if tweet['text'][0] != '@' :
            new_timeline.append((tweet['text'].encode('utf8'))+" From Twitter");
            
    return new_timeline
 
def login2renren():
    print 'print login2xiaonei <br>'
    verify_url = 'http://passport.renren.com/PLogin.do'
    verify_data = urllib.urlencode(
        {
        'domain':'renren.com',
        'email':  renren_usr,
        'password': renren_passwd,
        'origURL':'http://home.renren.com/Home.do',
        })
    result = urlfetch.fetch(
        url=verify_url,
        headers={'Cookie':make_cookie_header(cookie_buf),
                'Content-Type': 'application/x-www-form-urlencoded',
                'user-agent':'Mozilla/5.0 (Linux; U; Linux i686; en-US) AppleWebKit/525.13 (KHTML, like Gecko) Chrome/0.4.2.80 Safari/525.13', },
        method=urlfetch.POST,
        payload=verify_data,
        follow_redirects=False,
        )
    return result
 
def do_redirect(url, cookie):
    result = urlfetch.fetch(
        url=url,
        headers={'Cookie':make_cookie_header(cookie),
                'Content-Type': 'application/x-www-form-urlencoded',
                'user-agent':'Mozilla/5.0 (Linux; U; Linux i686; en-US) AppleWebKit/525.13 (KHTML, like Gecko) Chrome/0.4.2.80 Safari/525.13', },
        method=urlfetch.GET,
        follow_redirects=False,
        )
    return result
 
def send_status(status, cookie):
    status_url = 'http://status.renren.com/doing/update.do'
    status_data = urllib.urlencode({
        'c': status,
        'raw': status,
        'isAtHome': 0,
        })
    result = urlfetch.fetch(
        url=status_url,
        headers={
            'Cookie':make_cookie_header(cookie),
            'Content-Type': 'application/x-www-form-urlencoded',
            'user-agent':'Mozilla/5.0 (Linux; U; Linux i686; en-US) AppleWebKit/525.13 (KHTML, like Gecko) Chrome/0.4.2.80 Safari/525.13',
            'Referer': 'http://status.renren.com/ajaxproxy.htm'
        },
        method=urlfetch.POST,
        payload=status_data,
        )
    return result
 
class sync:
    def GET(s):
        global cookie_buf
        #get timeline
        print 'get timeline<br>'
        timeline = get_tweets(twitter_usr, twitter_passwd)
        if len(timeline) == 0:
            return 'no tweet to sync. <br>'
        
        
        #login to renren
        result = login2renren()
        cookie_buf = Cookie.SimpleCookie(result.headers.get('set-cookie', ''));
        callback_url = result.headers.get('location', 'xx');
 
        result = do_redirect(callback_url, cookie_buf)
 
        cookie_buf = Cookie.SimpleCookie(result.headers.get('set-cookie', ''))
        i = 0
        for tweet in timeline:
            i = i + 1
            if i == 10:
                break;
            result = send_status(tweet, cookie_buf)
            print "sync tweet:", tweet,"<br>"
        return 'ok'
    
    
def refresh():
        print 'refresh  '
        global cookie_buf
        #get timeline
        print 'get timeline'
        timeline = get_tweets(twitter_usr, twitter_passwd)
        if len(timeline) == 0:
            return 'no tweet to sync.'
        
        print 'print login2renren'
        #login to renren
        result = login2renren()
        cookie_buf = Cookie.SimpleCookie(result.headers.get('set-cookie', ''));
        callback_url = result.headers.get('location', 'xx');
 
        result = do_redirect(callback_url, cookie_buf)
 
        cookie_buf = Cookie.SimpleCookie(result.headers.get('set-cookie', ''))
        i = 0
        for tweet in timeline:
            i = i + 1
            if i == 10:
                break;
            result = send_status(tweet, cookie_buf)
            print 'tweet %d = %s' % (i, tweet);
            print "<br>"
        return 'ok'
    
def getTimeline():
     print 'get timeline'
     timeline = get_tweets(twitter_usr, twitter_passwd)
     if len(timeline) == 0:
         return 'no tweet to sync.'
     
     status=null
     
     for tweet in timeline:
            i = i + 1
            if i == 10:
                break;
            #result = send_status(tweet, cookie_buf)
            print 'tweet %d = %s' % (i, tweet);
            print "<br>"
            status+='tweet %d = %s' % (i, tweet)
            status+='<br>'
            
     return timeline
 
if __name__ == "__main__":
    print """<html>  <head>
    <link type="text/css" rel="stylesheet" href="/stylesheets/main.css" />
       <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
   </head>
  <body>
 """
    print 'main run<br>' 
    print 'app.cgirun();<br>'
    app.cgirun();
    #app.run();
    #sync();
    #refresh();
    #timeline = get_tweets(twitter_usr, twitter_passwd)
    #print getTimeline()
    #getTimeline()
    print 'Sync done<br>' 
    print """ </body>
    </html>"""
    
