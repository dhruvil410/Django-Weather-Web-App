import time
from time import sleep
from django.shortcuts import render,redirect
from django.db.utils import IntegrityError
from django.http import HttpResponse
from .models import country,city,hourly_forecast_log,daily_forecast_log,information
import requests
from django.contrib.auth.models import User,auth
from django.contrib import messages
from user.models import city as userCity,userInfo,todayData
from geopy import Nominatim
import os
from django.conf import settings


from pprint import pprint
import datetime as d

#home page
def home(request):
    with open(os.path.join(settings.BASE_DIR, 'ccdata.txt'),'r') as f:
        ccdata=f.readlines()
    ccdata=map(lambda x:x[:-1],ccdata)

    info=information()
    info.ccdata=ccdata
    info.city="Delhi"
    cityInfo=city.objects.get(city_name__iexact="Delhi")
    info.image=cityInfo.image
    info.country=cityInfo.country_id.country_name
    url = "http://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&appid={}&units=metric".format(cityInfo.latitude,
                                                                               cityInfo.longitude,"{Your OpenweatherMap API key}")
    data = requests.get(url).json()
    info.desc = data['weather'][0]['description'].upper()
    info.temp = data['main']['temp']
    info.temp = int(info.temp)
    info.humidity = data['main']['humidity']
    info.wind_speed = data['wind']['speed']
    try:
        info.wind_dir = data['wind']['deg']
    except:
        info.wind_dir=-1
    info.pressure = data['main']['pressure']/1000
    try:
        info.visibility = data['visibility']
    except:
        info.visibility=-1
    return render(request,"weather/home.html",{'info':info,'cityName':cityInfo.city_name})



#searchbar of home page
def search(request):
    with open(os.path.join(settings.BASE_DIR, 'ccdata.txt'),'r') as f:
        ccdata=f.readlines()
    ccdata=map(lambda x:x[:-1],ccdata)
    searchCity=request.POST['searchcity']
    info=information()
    try:
        geolocator = Nominatim()
        location = geolocator.geocode(searchCity)
        loc1 = geolocator.reverse("{}, {}".format(location.latitude, location.longitude))
        qcity=loc1.raw['address']['city']
        qcountry = loc1.raw['address']['country']
        url = "http://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&appid={}&units=metric".format(location.latitude,
                                                                                                      location.longitude,
                                                                                                      "{Your OpenweatherMap API key}")
        info.msg=""
    except:
        qcity="Delhi"
        qcountry="India"
        cityInfo = city.objects.get(city_name__iexact=qcity)
        info.msg="Please try other locations."
        url = "http://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&appid={}&units=metric".format(cityInfo.latitude,
                                                                                                      cityInfo.longitude,
                                                                                                      "{Your OpenweatherMap API key}")

    info.ccdata=ccdata
    info.city =qcity

    #info.image = cityInfo.image
    info.country = qcountry

    data = requests.get(url).json()
    info.desc = data['weather'][0]['description'].upper()
    info.temp = int(data['main']['temp'])
    info.humidity = data['main']['humidity']
    info.wind_speed = data['wind']['speed']
    try:
        info.wind_dir = data['wind']['deg']
    except:
        info.wind_dir = -1
    info.pressure = data['main']['pressure']/1000
    try:
        info.visibility = data['visibility']
    except:
        info.visibility = -1
    return render(request, "weather/home.html", {'info': info,'cityName':qcity})

#small admin page
def admin(request):
    return render(request,"weather/admin.html" ,{'what':'nothing'})

#hourly_forecast button of admin page
def hourly_forecast(request):

    print("{} Data Deleted".format(hourly_forecast_log.objects.all().delete()))
    cityObj=city.objects.all()
    i=0
    limit=0
    totalcity = len(cityObj)
    while i!=totalcity:
        x = cityObj[i]
        city_id=city.objects.get(pk=x.id)
        url = "http://api.openweathermap.org/data/2.5/onecall?lat={}&lon={}&appid={Your OpenweatherMap API key}&units=metric".format(x.latitude,x.longitude)
        try:
            data = requests.get(url).json()
        except:
            sleep(10)
            limit += 1
            print(limit)
            if limit != 5:
                continue
            else:
                print("Maybe your internet speed is slow now or maybe  your api call was finished ")
                print("only {} cities data updated".format(i + 1))
                break
        limit=0
        for idx,hour in enumerate(data['hourly']):
            if idx%3!=0:
                continue

            id=int(str(hour['dt'])+str(city_id.id%100000))
            desc=hour['weather'][0]['description']
            temp=hour['temp']
            humidity=hour['humidity']
            wind_speed=hour['wind_speed']
            try:
                wind_dir=hour['wind_deg']
            except:
                wind_dir=-1
            pressure=hour['pressure']
            try:
                visibility=hour['visibility']
            except:
                visibility=-1

            hr=(int(d.datetime.utcfromtimestamp(hour['dt']).strftime('%H'))+5) % 24
            try:
                hf = hourly_forecast_log.objects.create(id=id,
                                                        hour=hr,
                                                        city_id=city_id,desc=desc,temperature=temp,
                                                        humidity=humidity,wind_speed=wind_speed,
                                                        wind_dir=wind_dir,pressure=pressure,visibility=visibility)
            except IntegrityError:
                continue
        i+=1

    return render(request,"weather/admin.html" ,{'what':'hourly forecast'})

#daily_forecast button of admin page
def daily_forecast(request):
    cityObj = city.objects.all()
    totalcity=len(cityObj)
    print("{} Historical Data Deleted".format(daily_forecast_log.objects.filter(date=d.datetime.today().date() - d.timedelta(days=31)).delete()))
    print("{} Forecast Data Deleted".format(daily_forecast_log.objects.filter(date__gte=d.date.today()).delete()))
    limit=0
    i=0 
    while i!=totalcity:
        x=cityObj[i]
        start = d.datetime.today().date() - d.timedelta(days=1)
        end = d.datetime.today().date()
        city_id = city.objects.get(pk=x.id)
        id = int(str(city_id.id) + str(start).replace("-", ""))
        url = "https://api.weatherbit.io/v2.0/history/daily?lat={}&lon={}&start_date={}&end_date={}&key={}".format(
            x.latitude, x.longitude,
            str(start), str(end), "{Your WeatherBit API key}")
        url1="https://api.weatherbit.io/v2.0/forecast/daily?lat={}&lon={}&key={}".format(x.latitude, x.longitude,
                                                                                          "{Your WeatherBit API key}")
        try:
            data = requests.get(url).json()
            sleep(0.5)
            data1= requests.get(url1).json()
        except:
            sleep(10)
            limit+=1
            print(limit)
            if limit!=5:
                continue
            else:
                print("Maybe your internet speed is slow now or maybe  your api call was finished ")
                print("only {} cities data updated".format(i+1))
                break


        limit=0
        min_temp = data['data'][0]['min_temp']
        max_temp = data['data'][0]['max_temp']
        avg_humidity = data['data'][0]['rh']
        url = "https://api.weatherbit.io/v2.0/current?lat={}&lon={}&key={}".format(x.latitude, x.longitude,
                                                                                   "{Your WeatherBit API key}")
        data = requests.get(url).json()
        sunrise = str(data['data'][0]['sunrise']).split(":")
        sunset = str(data['data'][0]['sunset']).split(":")
        sunrise = d.datetime(1, 1, 1, int(sunrise[0]), int(sunrise[1])) + d.timedelta(hours=5, minutes=30)
        sunrise = sunrise.time()
        sunset = d.datetime(1, 1, 1, int(sunset[0]), int(sunset[1])) + d.timedelta(hours=5, minutes=30)
        sunset = sunset.time()
        daily_forecast_log.objects.create(id=id, date=start, city_id=city_id, min_temperature=min_temp,
                                          max_temperature=max_temp,
                                          avg_humidity=avg_humidity, sunrise_time=sunrise, sunset_time=sunset)
        data=data1
        for k in range(1,16):
            info = data['data'][k]
            sunrise = d.datetime.fromtimestamp(info['sunrise_ts']).time()
            sunset = d.datetime.fromtimestamp(info['sunset_ts']).time()
            min_temp = info['min_temp']
            max_temp = info['max_temp']
            avg_humidity = info['rh']
            date = d.datetime.today().date() + d.timedelta(days=k)
            id = int(str(city_id.id) + str(date).replace("-", ""))
            daily_forecast_log.objects.create(id=id, date=date, city_id=city_id, min_temperature=min_temp,
                                              max_temperature=max_temp,
                                          avg_humidity=avg_humidity, sunrise_time=sunrise, sunset_time=sunset)
        i+=1
    return render(request, "weather/admin.html", {'what': 'daily forecast'})

#daily_forecast_delete of admin page
def daily_forecast_delete(request):
    print("{} Data Deleted".format(daily_forecast_log.objects.all().delete()))
    return render(request, "weather/admin.html", {'what': 'daily forecast deleted'})


