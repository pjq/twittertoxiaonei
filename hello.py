#!/usr/bin/env python2.6
#coding=utf8
import cgi
import wsgiref.handlers

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext import db

import web
import Cookie, urllib
import simplejson as json
 
from google.appengine.api import urlfetch
from setting import app
from google.appengine.ext import db
from google.appengine.api import users

import code

import os
from google.appengine.ext.webapp import template

#twitter 帐号
user = 'twitter 帐号'
#twitter 密码
passwd = 'twitter 密码'

def composerStatus(dic):
    list=[]
    for i in dic:
         text = i['text']
         created_at = i['created_at']
         source=i['source']
         for v, k in i.items():
             if v == "user":                
                 name = k['name']              
                 profile_background_image_url = k['profile_background_image_url']
                 profile_image_url=k['profile_image_url']
                 followers_count = k['followers_count']
                 friends_count = k['friends_count']
                 favourites_count=k['favourites_count']
                 url=k['url']
                 statuses_count=k['statuses_count']
                 user_created_at=k['created_at']          
                
         status = " <img src=%s width=\"36\" height=\"36\"></img>%s <a href=%s>%s</a>(Tweet:%s,Followers:%s,Following: %s,Favourite:%s,Create At:%s)<br><prev>%s</prev> <br>"\
          % (profile_image_url, created_at, url,name,statuses_count, followers_count, friends_count, favourites_count,user_created_at,text)
         list.append(status.encode('utf8'))
    return list

def get_tweets (usr, passwd, timeline_type="user"):

    new_timeline = []
    
    if timeline_type == "user":
        timeline_uri = 'http://%s:%s@twitter.com/statuses/user_timeline.json?count=100&amp;since_id=%d' % (usr, passwd, 7057983358)
    elif timeline_type == "friends":        
        timeline_uri = 'http://%s:%s@twitter.com/statuses/friends_timeline.json?count=100&amp;' % (usr, passwd)
    timeline = urllib.urlopen(timeline_uri).read();
 
    timeline = json.loads(timeline)
    
    
    return composerStatus(timeline);
 
    if len(timeline) == 0:
        return []
    new_id = timeline[0]['id']
    if new_id == '' :
        return []
  
    for tweet in timeline:
        if tweet['text'][0] != '@' :
            new_timeline.append((tweet['text'].encode('utf8')));
    return new_timeline

class MainPage(webapp.RequestHandler):
  def get(self):
    self.response.out.write('<html><body>')
    
    self.response.out.write("""
          <form action="/sign" method="post">
            <div><textarea name="content" rows="3" cols="60"></textarea></div>
            <div><input type="submit" value="Sign Guestbook"></div>
          </form>
       """)

    greetings = db.GqlQuery("SELECT * FROM Greeting ORDER BY date DESC")

    for greeting in greetings:
      self.response.out.write('%s    ' % (greeting.date)) 
      if greeting.author:
        self.response.out.write('<b>%s</b> wrote:' % greeting.author.nickname())
      else:
        self.response.out.write('An anonymous person wrote:')
      
      self.response.out.write('<blockquote>%s</blockquote>' % 
                              cgi.escape(greeting.content))
      
    if users.get_current_user():
        greeting = Greeting.gql("WHERE author=:author ORDER BY content DESC", users.get_current_user())
    self.response.out.write('<b>The Current User msg:</b><br>')
    for greeting in greetings:
      self.response.out.write('%s    ' % (greeting.date)) 
      if greeting.author:
        self.response.out.write('<b>%s</b> wrote:' % greeting.author.nickname())
      else:
        self.response.out.write('An anonymous person wrote:')
      
      self.response.out.write('<blockquote>%s</blockquote>' % 
                              cgi.escape(greeting.content))

    # Write the submission form and the footer of the page

    
    self.response.out.write(""" </body>
      </html> """)
    
    
class MainPage2(webapp.RequestHandler):
  def get(self):
    greetings = Greeting.all().order('-date')
    #greetings=Greeting.gql('ORDER BY content DESC')

    if users.get_current_user():
      url = users.create_logout_url(self.request.uri)
      url_linktext = 'Logout'
    else:
      url = users.create_login_url(self.request.uri)
      url_linktext = 'Login'
      
    user_timeline = get_tweets(user, passwd, "user")
    friends_timeline = get_tweets(user, passwd, "friends")
    #timeline=['tweet a','tweet b']
    currentuser = users.get_current_user()
    
    #user_timeline=["%s %s" %() for text,user in user_timeline ]
 
    
    i = 0

    template_values = {
        'currentuser':currentuser,
        'friends_timeline':friends_timeline,
        'user_timeline':user_timeline,
      'greetings': greetings,
      'url': url,
      'url_linktext': url_linktext,
      }

    path = os.path.join(os.path.dirname(__file__), 'index.html')
    self.response.out.write(template.render(path, template_values))

class Greeting(db.Model):
    author = db.UserProperty()
    content = db.StringProperty(multiline=True)
    date = db.DateTimeProperty(auto_now_add=True)


class Guestbook(webapp.RequestHandler):
  def post(self):
    self.response.out.write('<html><body>You wrote:<pre>')
    self.response.out.write(cgi.escape(self.request.get('content')))
    self.response.out.write('</pre></body></html>')
    
    greeting = Greeting()
    
    if users.get_current_user():
        greeting.author = users.get_current_user();
    
    greeting.content = self.request.get('content')
    greeting.put()
    self.redirect('/')
    

def main():
  application = webapp.WSGIApplication(
                                       [('/', MainPage2),
                                        ('/sign', Guestbook)],
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
  main()
