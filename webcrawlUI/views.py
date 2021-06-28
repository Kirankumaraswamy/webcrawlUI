from django.shortcuts import render, redirect
import requests
import sys
from webcrawlUI.models import States, Cities, Weblinks, WebData
from webcrawlUI.helpers.qgram_index import QGramIndex
from django.http import JsonResponse
import urllib


# Create your views here.

def home(request):
    states = States.objects.all()
    context = {
        "states": states,
    }
    return render(request, 'webcrawlUI/home.html', context)


def cities(request, name):
    state = States.objects.filter(name=name)
    cities = Cities.objects.filter(state_id=state[0].id)
    for city in cities:
        city.web_count = Weblinks.objects.filter(city_id=city.id).count()
    context = {
        "cities": cities,
        "state_name": state[0].name,
    }
    return render(request, 'webcrawlUI/cities.html', context)


def city(request, state_name, city_name):
    city = Cities.objects.filter(name=city_name)
    weblinks = Weblinks.objects.filter(city_name=city_name)
    webdata = WebData.objects.filter(city_name=city_name)
    context = {
        "city_name": city[0].name,
        "state_name": state_name,
        "weblinks": weblinks,
        "webdata": webdata
    }
    return render(request, 'webcrawlUI/city.html', context)

def searchCities(request, values):
    values = urllib.parse.unquote(values)
    print(values)
    obj = QGramIndex.getInstance()
    prefix = obj.normalize(values)
    delta = int(len(prefix) / 4)
    print(obj.wiki_data)
    matches = obj.find_matches(prefix, delta)
    responseData = {
        'data': matches
    }
    return JsonResponse(responseData)

def renderCity(request, city):
    unquote_city = urllib.parse.unquote(city)
    city = Cities.objects.filter(name=unquote_city)
    if len(city) != 0:
        city_name = city[0].name
        state_name = city[0].state_name
        data = state_name + "/" + city_name
        data = urllib.parse.quote(data, safe="")
    else:
        data = ""
    responseData = {
        'data': data
    }
    return JsonResponse(responseData)

def run_web_crawl_task(request, state_name, city_name):
    url = 'http://127.0.0.1:6800/schedule.json'
    myobj = {'project': 'webCrawl', 'spider': 'webCrawl', 'state': state_name, 'city': city_name}
    x = requests.post(url, data=myobj)
    if city_name != "null":
        return redirect('/webCrawl/' + state_name + '/' + city_name)
    elif state_name != "null":
        return redirect('/webCrawl/' + state_name)
    else:
        return redirect('/webCrawl')


def run_google_spider(request, state_name, city_name):
    url = 'http://127.0.0.1:6800/schedule.json'
    myobj = {'project': 'webCrawl', 'spider': 'googleSearch', 'state': state_name, 'city': city_name}
    x = requests.post(url, data=myobj)
    if city_name != "null":
        return redirect('/webCrawl/' + state_name + '/' + city_name)
    elif state_name != "null":
        return redirect('/webCrawl/' + state_name)
    else:
        return redirect('/webCrawl')


def generate_cities_spider(request, id):
    url = 'http://127.0.0.1:6800/schedule.json'
    print("Generating cities for ", id)
    myobj = {'project': 'webCrawl', 'spider': 'generateCities', 'domains': 'abcdef'}
    x = requests.post(url, data=myobj)

    return redirect('/webCrawl')
