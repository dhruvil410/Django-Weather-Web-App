from django.db import models
from django.db.models import QuerySet

from weather.models import city as ci
class city(models.Model):
    username=models.CharField(primary_key=True,max_length=40)
    city_id=models.ForeignKey(ci,on_delete=models.CASCADE)

class signup():
    username : str
    city : str
    email : str
    ccdata: list

class userInfo():
    username : str
    city : str
    country : str
    image : str

class todayData():
    hour : int
    desc : str
    icon : str
    temperature : float
    humidity : int
    wind_speed : float
    wind_dir : float
    pressure : int
    visibility : int

class forecast():
    fD : QuerySet
    day : list
    date : list
