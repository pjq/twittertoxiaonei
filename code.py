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
 
def make_cookie_header(cookie):
    ret = ''
    for v in cookie.values():
        ret += '%s=%s;' % (v.key, v.value)
    return ret
 
def get_tweets (usr, passwd):
    last_tweet_id = 0
    last_tweet_record = None
    last_tweet_records = db.GqlQuery('SELECT * FROM LastTweetRecord');
    for record in last_tweet_records:
        try:
            last_tweet_id = int(record.id)
            last_tweet_record = record
        except Exception, e:
            last_tweet_id = 1
 
    if last_tweet_records.count() == 0:
        last_tweet_id = 1
        last_tweet_record = LastTweetRecord()
        last_tweet_record.put()
 
    new_timeline = []
    timeline_uri = 'http://%s:%s@twitter.com/statuses/user_timeline.json?count=100&amp;since_id=%d' % (usr, passwd, last_tweet_id)
    timeline = urllib.urlopen(timeline_uri).read();
 
    timeline = json.loads(timeline)
 
    if len(timeline) == 0:
        return []
    new_id = timeline[0]['id']
    if new_id == '' :
        return []
 
    last_tweet_record.id = str(new_id)
    db.put(last_tweet_record)
 
    for tweet in timeline:
        if tweet['text'][0] != '@' :
            new_timeline.append((tweet['text'].encode('utf8') ));
    return new_timeline
 
def login2renren():
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
        i=0
        for tweet in timeline:
            i=i+1
            #if i==1:
            #    break;
            result = send_status(tweet, cookie_buf)
        return 'ok'
    
    
def refresh():
        global cookie_buf
        #get timeline
        print 'get timeline'
        
        timeline=['test1','test2'];
   
   
        result = login2renren()
        cookie_buf = Cookie.SimpleCookie(result.headers.get('set-cookie', ''));
        callback_url = result.headers.get('location', 'xx');
 
        result = do_redirect(callback_url, cookie_buf)
 
        cookie_buf = Cookie.SimpleCookie(result.headers.get('set-cookie', ''))
        for tweet in timeline:
            result = send_status(tweet, cookie_buf)
        return 'ok'
 
if __name__ == "__main__":
    print 'main run'
    app.cgirun();
    '''app.run();'''
    #sync();
    #refresh();
    #timeline = get_tweets(twitter_usr, twitter_passwd)
    #print timeline
    print 'Sync done' 
    
