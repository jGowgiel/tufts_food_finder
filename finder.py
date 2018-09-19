from flask import Flask, render_template, request
from werkzeug.contrib.cache import MemcachedCache

import requests
import datetime

app = Flask(__name__)
cache = MemcachedCache(['127.0.0.1:11211'])

ROOT_API = 'https://tuftsdiningdata.herokuapp.com/menus/'

# At most, look two weeks in advance
MAX_DAYS = 14

LOCATIONS = ['dewick', 'carm', 'hodgdon']


@app.route('/')
def index():

    search_term = request.args.get('search', '')

    # If the index is requested with a search term, perform the search
    if search_term:

        results = find_food(search_term)
        print(results)
        return render_template('results.html', keyword=search_term, results=results)

    else:
        return render_template('index.html')


def find_food(keyword):

    # Getting the date range:
    date_list = [(datetime.datetime.today() + datetime.timedelta(days=x)) for x in range(0, MAX_DAYS)]
    results = {}
    for date in date_list:
        date_part = date.strftime("%d/%m/%Y")

        for location in LOCATIONS:
            menu_identifier = location + '/' + date_part
            cached_menu = cache.get(menu_identifier)

            if cached_menu:
                menu = cached_menu
            else:
                menu = requests.get(ROOT_API + menu_identifier).json()
                cache.set(location + '/' + date_part, menu, timeout=(60 * 60 * 24))

            # Search the menu
            matches = find_keyword(keyword, menu)

            if matches:
                results[location] = {
                    'matches': find_keyword(keyword, menu),
                    'date': date.strftime("%A, %B %d")
                }
    return results


def find_keyword(keyword, menu):
    found_foods = []
    for meal_period in menu['data'].values():
        for food_group in meal_period.values():
            found_foods += [match for match in food_group if keyword.lower() in match.lower()]
    return found_foods
