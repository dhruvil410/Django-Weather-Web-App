from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('search', views.search, name="search"),
    path('qwertyuiop', views.admin, name="qwertyuiop"),
    path('hourly_forecast', views.hourly_forecast, name="hourly_forecast"),
    path('daily_forecast', views.daily_forecast, name="daily_forecast"),
    path('daily_forecast_delete', views.daily_forecast_delete, name="daily_forecast_delete")
]
