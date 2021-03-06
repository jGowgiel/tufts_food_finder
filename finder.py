from flask import Flask, render_template, request
from flask_caching import Cache

import os
import requests
import datetime
import html

app = Flask(__name__)
cache = Cache()

### Cache config from https://devcenter.heroku.com/articles/memcachier#flask

cache_servers = os.environ.get('MEMCACHIER_SERVERS')
if cache_servers == None:
    # Fall back to simple in memory cache (development)
    cache.init_app(app, config={'CACHE_TYPE': 'simple'})
else:
    cache_user = os.environ.get('MEMCACHIER_USERNAME') or ''
    cache_pass = os.environ.get('MEMCACHIER_PASSWORD') or ''
    cache.init_app(app,
        config={'CACHE_TYPE': 'saslmemcached',
                'CACHE_MEMCACHED_SERVERS': cache_servers.split(','),
                'CACHE_MEMCACHED_USERNAME': cache_user,
                'CACHE_MEMCACHED_PASSWORD': cache_pass,
                'CACHE_OPTIONS': { 'behaviors': {
                    # Faster IO
                    'tcp_nodelay': True,
                    # Keep connection alive
                    'tcp_keepalive': True,
                    # Timeout for set/get requests
                    'connect_timeout': 2000, # ms
                    'send_timeout': 750 * 1000, # us
                    'receive_timeout': 750 * 1000, # us
                    '_poll_timeout': 2000, # ms
                    # Better failover
                    'ketama': True,
                    'remove_failed': 1,
                    'retry_timeout': 2,
                    'dead_timeout': 30}}})

### End cache config

ROOT_API = 'https://tuftsdiningdata.herokuapp.com/menus/'

# At most, look one week in advance
MAX_DAYS = 5

CACHE_TIME = 60 * 60 * 24 * 7

LOCATIONS = ['dewick', 'carm', 'hodgdon']


@app.route('/')
def index():

    search_term = request.args.get('search', '')

    # If the index is requested with a search term, perform the search
    if search_term:

        results = find_food(search_term)
        return render_template('results.html', keyword=search_term, results=results)

    else:
        return render_template('index.html')

@app.route('/about')
def about():

    return render_template('about.html')

def find_food(keyword):

    # Getting the date range:
    date_list = [(datetime.datetime.today() + datetime.timedelta(days=x)) for x in range(0, MAX_DAYS)]
    results = {}
    for date in date_list:
        date_part = date.strftime("%d/%m/%Y")

        for location in LOCATIONS:
            menu_identifier = location + '/' + date_part
            menu = cache.get(menu_identifier)

            if not menu:
                menu = requests.get(ROOT_API + menu_identifier).json()
                cache.set(location + '/' + date_part, menu, timeout=CACHE_TIME)

            # Search the menu
            matches = find_keyword(keyword, menu)


            if matches:
                results[location.capitalize()] = {
                    'matches': find_keyword(keyword, menu),
                    'date': date.strftime("%A, %B %d")
                }
    return results


def find_keyword(keyword, menu):
    found_foods = []
    for meal_period in menu['data']:
        for food_group in menu['data'][meal_period].values():
            found_foods += [(html.unescape(match + ' during ' + meal_period.lower())) for match in food_group if keyword.lower() in match.lower()]
    return found_foods









