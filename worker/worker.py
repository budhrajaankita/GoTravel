#from celery import Celery
#from datetime import datetime
#import requests
#import os
#import json


#CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL')
#CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND')
#OW_API_KEY = os.environ.get('OW_API_KEY')

#celery_app = Celery(name='worker',
#                    broker=CELERY_BROKER_URL,
#                    result_backend=CELERY_RESULT_BACKEND)


#@celery_app.task
##def get_weather(destination, planned_date):
##    try:
##        # Convert the destination into exact geographical coordinates (latitude, longitude)
##        resp_geo = requests.get(
##            f"http://api.openweathermap.org/geo/1.0/direct?q={destination}&limit=1&appid={OW_API_KEY}")
##        geo_data = resp_geo.json()
##        lat, lon = geo_data[0]["lat"], geo_data[0]["lon"]

##        # Get the weather information of the destination
##        resp_weather = requests.get(
##            f"http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={OW_API_KEY}")
##        weather_data = resp_weather.json()

##        # Filter weather data based on the planned_date
##        planned_date_format = datetime.strptime(
##            planned_date, "%Y-%m-%dT%H:%M:%S")
##        # print(f"planned_date_format: {planned_date_format}", flush=True)
##        # print(f"planned_date_format_type: {type(planned_date_format)}", flush=True)
##        relevant_forecast = None
##        for forecast in weather_data['list']:
##            forecast_date = datetime.strptime(
##                forecast['dt_txt'], "%Y-%m-%d %H:%M:%S")
##            # print(f"forecast_date: {forecast_date}", flush=True)
##            # print(f"forecast_date_type: {type(forecast_date)}", flush=True)
##            if forecast_date == planned_date_format:
##                relevant_forecast = forecast
##                break

##        if relevant_forecast:
##            # convert Kelvin to Celsius and only keep one decimal place
##            temperature = round(relevant_forecast['main']['temp'] - 273.15, 1)
##            weather = relevant_forecast['weather'][0]['description']
##            return json.dumps(f"Temperature: {temperature}°C, Weather: {weather}")
##        return json.dumps(f"Error: No forecast data found for {planned_date_format}. Only 5-day forecast available")
##    except Exception as e:
##        return f"Error: Something went wrong when getting weather details - {str(e)}"
