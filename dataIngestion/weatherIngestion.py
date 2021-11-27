import requests
from extensions import mongo_client, os
from datetime import datetime
from bson.objectid import ObjectId
from .config import *

FORECASTED_WEATHER_CALL = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/[city_name]?unitGroup=us&key=" \
                          + os.environ.get('VISUAL_CROSSINGS_KEY')
HISTORICAL_WEATHER_CALL = ""


# retrieveHistoricalWeatherData
# inputs: city name
# output: a json dataset of the data from the VisualCrossing's API
def retrieve_historical_weather_data(city_name):
    historical_weather = mongo_client.db.HistoricalWeather


# retrieveForecastedWeatherData
# inputs: city name
# output: a json dataset of the data from the VisualCrossing's API containing a
#         city's forecasted weather in fahrenheit of the next 14 days. Also contains
#         the current day fyi. Weather conditions are also given.
def retrieve_forecasted_weather_data(city_name):
    forecasted_weather_call = FORECASTED_WEATHER_CALL.replace("[city_name]", city_name)
    response = requests.get(url=forecasted_weather_call)
    data = response.json()['days']
    forecasts = {}
    for day in data:
        forecast = dict(temperature=day['temp'],
                        conditions=day['conditions'],
                        )
        forecast_datetime = datetime.strptime(day['datetime'] + "T00:00:00Z", '%Y-%m-%dT%H:%M:%SZ')
        forecasts[forecast_datetime] = forecast
    return forecasts
