from django.contrib import admin
from .models import city,country,hourly_forecast_log,daily_forecast_log

admin.site.register(city)
admin.site.register(country)
admin.site.register(hourly_forecast_log)
admin.site.register(daily_forecast_log)