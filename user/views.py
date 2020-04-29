import os
from django.conf import settings
from geopy import Nominatim
from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.models import User,auth
from django.contrib import messages
from weather.models import city, country, hourly_forecast_log, daily_forecast_log, information
from .models import city as userCity, userInfo, todayData, forecast
from .models import signup
import requests
import datetime as d
def signUP(request):
    data=signup()
    if request.method=='POST':
        # if request is post,create user with POST data
        username=request.POST['username']
        data.username=username
        password = request.POST['password']
        repassword = request.POST['repassword']
        email = request.POST['email']
        city_name=request.POST['city']
        data.city=city_name
        data.email=email
        data.ccdata = list(map(lambda x: x['city_name'], city.objects.values('city_name')))
        if len(city_name.strip()) < 2:
            messages.info(request, "Enter Valid City Name")
            return render(request,'user/signUP.html',{'data':data})
        city_name=city_name[0].upper()+city_name[1:]
        if User.objects.filter(username=username).exists():
            messages.info(request,"Username Already Exists!")
            return render(request,'user/signUP.html',{'data':data})
        if User.objects.filter(email=email).exists():
            messages.info(request, "Email ID Already Exists!")
            return render(request,'user/signUP.html',{'data':data})
        elif len(password.strip())<5 or len(password.strip())>20:
            messages.info(request, "Password length must be between 6-20 characters.")
            return render(request,'user/signUP.html',{'data':data})
        elif password.strip() != repassword.strip():
            messages.info(request, "Password and Confirm Password must be same.")
            return render(request,'user/signUP.html',{'data':data})
        elif not city.objects.filter(city_name=city_name).exists():
            User.objects.create_user(username=username, email=email, password=password)
            cityid = 100001 #Default Mumbai
            userCity.objects.create(username=username, city_id=cityid)
            messages.info(request, "City not available. Your account created with Default city as Mumbai, India")
            return redirect('/')
        else:
            #create_user
            User.objects.create_user(username=username,email=email,password=password)
            cityid = city.objects.get(city_name=city_name)
            userCity.objects.create(username=username,city_id=cityid)
            return redirect('/')
    else:
        # if request is get,render singUP page
        messages.info(request,"")
        data.ccdata = sorted(list(map(lambda x: x['city_name'], city.objects.values('city_name'))))
        return render(request,"user\signUP.html",{'data':data})
def signIN(request):
    if request.method == 'POST':
        # if request is post ,sign in with POST data
        username=request.POST['username']
        password=request.POST['password']

        if User.objects.filter(username=username).exists() or User.objects.filter(email=username).exists():
            if User.objects.filter(username=username).exists():
                pass
            else:
                username=User.objects.get(email=username).username
            user=auth.authenticate(username=username,password=password)
            if user is not None:
                auth.login(request,user)
                uI = userInfo()
                uI.username = username
                uI.city = userCity.objects.get(username=username).city_id.city_name
                cityid = userCity.objects.get(username=username).city_id.pk
                uI.country = city.objects.get(pk=cityid).country_id.country_name
                uI.image = city.objects.get(pk=cityid).image
                info=currdata(uI.city)
                fD = forecastData(cityid)
                hD = historicData(cityid)
                date=list(map(lambda x: x['date'].strftime('%d %b'),fD.values('date')))
                day=list(map(lambda x: x['date'].strftime('%A'),fD.values('date')))
                fcD=zip(day,date,fD)
                date = list(map(lambda x: x['date'].strftime('%d %b'), hD.values('date')))
                day = list(map(lambda x: x['date'].strftime('%A'), hD.values('date')))
                hcD = zip(day, date, hD)
                hR = hourlyReport(cityid)

                return render(request,"user/userHome.html",
                              {'userInfo': uI, 'hrfc': hR, 'forecastData': fcD,'historicData':hcD,'info':info})


            else:
                messages.info(request, "Incorrect Password")
                return redirect('/')

        else:
            messages.info(request, "Username or E-mail not found")
            return redirect('/')
    else:
        return render(request, "weather/home.html")

def logOut(request):
    auth.logout(request)
    return redirect('/')

#searchbar of userhome page
def searchbar(request):
    uI=userInfo()
    uI.username=request.POST.get('usrnm','Search')
    iconDict = {'thunderstorm with light rain': '7.png', 'thunderstorm with rain': '7.png',
                'thunderstorm with heavy rain': '7.png', 'light thunderstorm': '7.png',
                'thunderstorm': '7.png', 'heavy thunderstorm': '7.png', 'ragged thunderstorm': '7.png',
                'thunderstorm with light drizzle': '7.png',
                'thunderstorm with drizzle': '7.png', 'thunderstorm with heavy drizzle': '7.png',
                'light intensity drizzle': '5.png', 'drizzle': '5.png',
                'heavy intensity drizzle': '5.png', 'light intensity drizzle rain': '5.png', 'drizzle rain': '5.png',
                'heavy intensity drizzle rain': '5.png',
                'shower rain and drizzle': '5.png', 'heavy shower rain and drizzle': '5.png', 'shower drizzle': '5.png',
                'light rain': '6.png',
                'moderate rain': '6.png', 'heavy intensity rain': '6.png', 'very heavy rain': '6.png',
                'extreme rain': '6.png', 'freezing rain': '8.png',
                'light intensity shower rain': '5.png', 'shower rain': '5.png', 'heavy intensity shower rain': '5.png',
                'ragged shower rain': '5.png',
                'light snow Snow': '8.png', 'heavy snow': '8.png', 'Sleet': '8.png', 'light shower sleet': '8.png',
                'shower sleet': '8.png',
                'light rain and snow': '8.png', 'rain and snow': '8.png', 'light shower snow': '8.png',
                'shower snow': '8.png', 'heavy shower snow': '8.png',
                'mist': '9.png', 'smoke': '9.png', 'haze': '9.png', 'sand / dust whirls': '9.png', 'fog': '9.png',
                'sand': '9.png', 'dust': '9.png',
                'volcanic ash': '9.png', 'squalls': '9.png', 'tornado': '9.png', 'clear sky': '1.png',
                'few clouds': '2.png', 'scattered clouds': '3.png',
                'broken clouds': '4.png', 'overcast clouds': '4.png'}

    searchCity=request.POST['city_name']
    info=information()

    try:
        cityInfo=city.objects.get(city_name=searchCity)
        url = "http://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&appid={}&units=metric".format(cityInfo.latitude,
                                                                                                     cityInfo.longitude,
                                                                                              "{Your OpenweatherMap API key}")
        cityid = cityInfo.id
        qcity = cityInfo.city_name
        qcountry="India"
        info.msg=""

    except:
        info.msg="Please search other locations..."
        cityInfo = city.objects.get(city_name__iexact="Delhi")
        cityid=cityInfo.id
        url = "http://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&appid={}&units=metric".format(
            cityInfo.latitude,
            cityInfo.longitude,
            "{Your OpenweatherMap API key}")
        qcity = "Delhi"
        qcountry = "India"

    info.ccdata = list(map(lambda x:x['city_name'],city.objects.values('city_name')))
    info.city =qcity
    info.country = qcountry
    fD = forecastData(cityid)
    date = list(map(lambda x: x['date'].strftime('%d %b'), fD.values('date')))
    day = list(map(lambda x: x['date'].strftime('%A'), fD.values('date')))
    fcD = zip(day, date, fD)
    hR = hourlyReport(cityid)
    data = requests.get(url).json()
    info.desc = data['weather'][0]['description'].upper()
    try:
        infoimg=iconDict['{}'.format(info.desc.lower())]
        info.image = "user/image/"+infoimg
    except:
        info.image='user/image/forecast.png'

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


    return render(request, "user/userHome.html", {'info': info,'userInfo':uI,'forecastData':fcD,'hrfc':hR})
#current weather of user home page
def currdata(city_name):
    iconDict = {'thunderstorm with light rain': '7.png', 'thunderstorm with rain': '7.png',
                'thunderstorm with heavy rain': '7.png', 'light thunderstorm': '7.png',
                'thunderstorm': '7.png', 'heavy thunderstorm': '7.png', 'ragged thunderstorm': '7.png',
                'thunderstorm with light drizzle': '7.png',
                'thunderstorm with drizzle': '7.png', 'thunderstorm with heavy drizzle': '7.png',
                'light intensity drizzle': '5.png', 'drizzle': '5.png',
                'heavy intensity drizzle': '5.png', 'light intensity drizzle rain': '5.png', 'drizzle rain': '5.png',
                'heavy intensity drizzle rain': '5.png',
                'shower rain and drizzle': '5.png', 'heavy shower rain and drizzle': '5.png', 'shower drizzle': '5.png',
                'light rain': '6.png',
                'moderate rain': '6.png', 'heavy intensity rain': '6.png', 'very heavy rain': '6.png',
                'extreme rain': '6.png', 'freezing rain': '8.png',
                'light intensity shower rain': '5.png', 'shower rain': '5.png', 'heavy intensity shower rain': '5.png',
                'ragged shower rain': '5.png',
                'light snow Snow': '8.png', 'heavy snow': '8.png', 'Sleet': '8.png', 'light shower sleet': '8.png',
                'shower sleet': '8.png',
                'light rain and snow': '8.png', 'rain and snow': '8.png', 'light shower snow': '8.png',
                'shower snow': '8.png', 'heavy shower snow': '8.png',
                'mist': '9.png', 'smoke': '9.png', 'haze': '9.png', 'sand / dust whirls': '9.png', 'fog': '9.png',
                'sand': '9.png', 'dust': '9.png',
                'volcanic ash': '9.png', 'squalls': '9.png', 'tornado': '9.png', 'clear sky': '1.png',
                'few clouds': '2.png', 'scattered clouds': '3.png',
                'broken clouds': '4.png', 'overcast clouds': '4.png'}
    searchCity = city_name
    info = information()
    try:
        cityInfo = city.objects.get(city_name__iexact=searchCity)
        url = "http://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&appid={}&units=metric".format(
            cityInfo.latitude,
            cityInfo.longitude,
            "{Your OpenweatherMap API key}")
        qcity = cityInfo.city_name
        qcountry = "India"
    except:
        cityInfo = city.objects.get(city_name__iexact="Mumbai")
        url = "http://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&appid={}&units=metric".format(
            cityInfo.latitude,
            cityInfo.longitude,
            "{Your OpenweatherMap API key}")
        qcity="Mumbai"
        qcountry="India"

    info.ccdata = sorted(list(map(lambda x:x['city_name'],city.objects.values('city_name'))))
    info.city = qcity
    info.country = qcountry

    data = requests.get(url).json()
    info.desc = data['weather'][0]['description'].upper()
    try:
        infoimg = iconDict['{}'.format(info.desc.lower())]
        info.image = 'user/image/{}'.format(infoimg)
    except:
        info.image = 'user/image/forecast.png'

    info.temp = int(data['main']['temp'])
    info.humidity = data['main']['humidity']
    info.wind_speed = data['wind']['speed']
    try:
        info.wind_dir = data['wind']['deg']
    except:
        info.wind_dir = -1
    info.pressure = data['main']['pressure'] / 1000
    try:
        info.visibility = data['visibility']
    except:
        info.visibility = -1

    return info

#hourly report of user home page
def hourlyReport(cityid):
    iconDict = {'thunderstorm with light rain': '7.png', 'thunderstorm with rain': '7.png',
                'thunderstorm with heavy rain': '7.png', 'light thunderstorm': '7.png',
                'thunderstorm': '7.png', 'heavy thunderstorm': '7.png', 'ragged thunderstorm': '7.png',
                'thunderstorm with light drizzle': '7.png',
                'thunderstorm with drizzle': '7.png', 'thunderstorm with heavy drizzle': '7.png',
                'light intensity drizzle': '5.png', 'drizzle': '5.png',
                'heavy intensity drizzle': '5.png', 'light intensity drizzle rain': '5.png', 'drizzle rain': '5.png',
                'heavy intensity drizzle rain': '5.png',
                'shower rain and drizzle': '5.png', 'heavy shower rain and drizzle': '5.png', 'shower drizzle': '5.png',
                'light rain': '6.png',
                'moderate rain': '6.png', 'heavy intensity rain': '6.png', 'very heavy rain': '6.png',
                'extreme rain': '6.png', 'freezing rain': '8.png',
                'light intensity shower rain': '5.png', 'shower rain': '5.png', 'heavy intensity shower rain': '5.png',
                'ragged shower rain': '5.png',
                'light snow Snow': '8.png', 'heavy snow': '8.png', 'Sleet': '8.png', 'light shower sleet': '8.png',
                'shower sleet': '8.png',
                'light rain and snow': '8.png', 'rain and snow': '8.png', 'light shower snow': '8.png',
                'shower snow': '8.png', 'heavy shower snow': '8.png',
                'mist': '9.png', 'smoke': '9.png', 'haze': '9.png', 'sand / dust whirls': '9.png', 'fog': '9.png',
                'sand': '9.png', 'dust': '9.png',
                'volcanic ash': '9.png', 'squalls': '9.png', 'tornado': '9.png', 'clear sky': '1.png',
                'few clouds': '2.png', 'scattered cloud': '3.png',
                'broken clouds': '4.png', 'overcast clouds': '4.png'}
    hR=[]
    obj=hourly_forecast_log.objects.filter(city_id=cityid)
    y,m,dt = d.datetime.today().strftime('%Y'),d.datetime.today().strftime('%m'),d.datetime.today().strftime('%d')
    timestamp=int(d.datetime.timestamp(d.datetime(int(y),int(m),int(dt))))
    timestamp2=int(d.datetime.timestamp(d.datetime(int(y),int(m),int(dt)+1)))
    hid=int(str(timestamp)+str(cityid%100000))
    hid2=int(str(timestamp2)+str(cityid%100000))
    #obj=obj.filter(id__gt=hid).filter(id__lt=hid2).order_by('id')
    for i in obj[:8]:
        hourlyData=todayData()
        hourlyData.hour=i.hour
        hourlyData.desc=i.desc
        try:
            hourlyData.icon='user/image/'+iconDict[hourlyData.desc.lower()]
        except:
            hourlyData.icon="user/image/1.png"
        hourlyData.temperature=i.temperature
        hourlyData.humidity=i.humidity
        hourlyData.wind_speed=i.wind_speed
        hourlyData.wind_dir=i.wind_dir
        hourlyData.pressure=i.pressure
        hourlyData.visibility=i.visibility
        hR.append(hourlyData)
    print(len(hR))
    return hR

#forecast data of userhome page
def forecastData(cityid):
    obj=daily_forecast_log.objects.filter(city_id=cityid)
    pD=obj.filter(date__gt=d.date.today())
    fD=pD.filter(date__lt=d.date.today()+d.timedelta(days=9))
    fD=fD.order_by('date')
    return fD
#historic data of userhome page
def historicData(cityid):
    obj=daily_forecast_log.objects.filter(city_id=cityid)
    pD=obj.filter(date__lt=d.date.today())
    fD=pD.filter(date__gt=d.date.today()-d.timedelta(days=9))
    fD=fD.order_by('-date')
    return fD





