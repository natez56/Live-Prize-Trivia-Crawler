from google.appengine.ext import ndb
import requests_toolbelt.adapters.appengine
import webapp2
import logging
import string
import random
import json
import jinja2
import time
import requests

# Used to enable the requests library.
requests_toolbelt.adapters.appengine.monkeypatch()

env = jinja2.Environment(
    loader=jinja2.PackageLoader('main', 'templates'),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class Home(webapp2.RequestHandler):
    def get(self):
        items = []
        score_file = 'score_file.txt'

        with open(score_file, 'r') as f:
            item = {}
            team_position = 1
            for x in f:
                x = x.rstrip()
                if "Name" in x:
                    x = x.replace("Name: ", "")
                    item = dict(name=str(team_position) + ") " + x)
                    team_position += 1
                else:
                    x = x.replace("Score: ", "")
                    item["score"] = x
                    items.append(item)

        # Template values added to index.html
        template = env.get_template('index.html')

        self.response.write(template.render(items=items))


routes = [
    webapp2.Route(r'/', handler=Home, name='home'),
]

app = webapp2.WSGIApplication(routes, debug=True)
