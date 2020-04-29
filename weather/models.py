from django.db import models

class country(models.Model):
    id=models.IntegerField(primary_key=True)
    country_name=models.CharField(max_length=40)


class city(models.Model):
    id=models.IntegerField(primary_key=True)
    city_name=models.CharField(max_length=40)
    image=models.ImageField(upload_to="cities")
    longitude=models.FloatField()
    latitude=models.FloatField()
    country_id=models.ForeignKey(country,on_delete=models.CASCADE)

class hourly_forecast_log(models.Model):
    id=models.IntegerField(primary_key=True)
    hour=models.IntegerField()
    city_id=models.ForeignKey(city,on_delete=models.CASCADE)
    desc=models.CharField(max_length=40)
    temperature=models.FloatField()
    humidity=models.IntegerField()
    wind_speed=models.FloatField()
    wind_dir=models.IntegerField(null=True)
    pressure=models.IntegerField()
    visibility=models.IntegerField()

class daily_forecast_log(models.Model):
    id=models.BigIntegerField(primary_key=True)
    date=models.DateField()
    city_id=models.ForeignKey(city,on_delete=models.CASCADE)
    min_temperature=models.FloatField()
    max_temperature=models.FloatField()
    avg_humidity=models.FloatField()
    sunrise_time=models.TimeField()
    sunset_time=models.TimeField()

class information():
    city : str
    country : str
    image : str
    desc : str
    temp : float
    humidity : int
    wind_speed : float
    wind_dir : int
    pressure : int
    visibility : int
    ccdata : list
    msg : str