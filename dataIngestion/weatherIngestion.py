import requests
from extensions import mongo_client, os
from datetime import datetime, timedelta, date as dt
from bson.objectid import ObjectId
from .config import *


FORECASTED_WEATHER_CALL = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/[city_name]?unitGroup=us&key=" \
                          + os.environ.get('VISUAL_CROSSINGS_KEY') + "&options=nonulls"
HISTORICAL_WEATHER_CALL = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/[city_name]/[from_date]/[to_date]?unitGroup=us&key=" \
                          + os.environ.get('VISUAL_CROSSINGS_KEY') + "&options=nonulls&include=obs%2Cstats"


# retrieveHistoricalWeatherData
# inputs: city name
# output: a json dataset of the data from the VisualCrossing's API
def retrieve_historical_weather_data(city_name):
    historical_weather = mongo_client.db.HistoricalWeather

    # finds the most recent date in the database
    try:
        most_recent_date = (historical_weather.find({}, {'datetime': 1}).sort([('datetime', -1)]).limit(1))[0]['datetime']
        print(most_recent_date)
    except:
        most_recent_date = None

    historical_weather_call = HISTORICAL_WEATHER_CALL.replace("[city_name]", city_name)
    # Making starting point yesterday
    to_date = dt.today() - timedelta(days=1)
    older_dates_found = False

    # Empty dict for storing date data
    historical_dates_data = {}

    # For loop for acquiring the last two years - incrementing weekly
    for date in range(104):  # todo SET to 104
        # if older dates are found in db then stop
        if older_dates_found:
            break

        # Setting the from_date back two weeks
        from_date = to_date - timedelta(weeks=1)
        # Inserting correct dates
        historical_weather_call = historical_weather_call.replace("[from_date]", from_date.strftime('%Y-%m-%d')).replace("[to_date]", to_date.strftime('%Y-%m-%d'))

        # Setting new URL
        try:
            response = requests.get(url=historical_weather_call)
        except:
            return response.reason

        # Acquiring days
        days = response.json()['days']

        # Going through each day and adding it to dict
        # Reversed for db date comparison
        for day in reversed(days):
            historical_data = dict(temperature=day['temp'],
                                   precipitation=day['precip'],
                                   conditions=day['conditions']
                                   )
            historical_datetime = day['datetime']
            # Checking if date is already in db to reduce redundancy
            if most_recent_date is not None and most_recent_date >= datetime.strptime(historical_datetime + "T00:00:00Z", '%Y-%m-%dT%H:%M:%SZ'):
                older_dates_found = True
                break
            historical_dates_data[historical_datetime] = historical_data

        # Inserted back [from_date] and [to_date] so the next dates can be added in the next loop iteration
        historical_weather_call = historical_weather_call.replace(from_date.strftime('%Y-%m-%d'), "[from_date]").replace(to_date.strftime('%Y-%m-%d'), "[to_date]")
        to_date = from_date

    # Adding historical data to db
    for date in historical_dates_data:
        historical_datetime = datetime.strptime(date + "T00:00:00Z", '%Y-%m-%dT%H:%M:%SZ')
        mongo_client.db.HistoricalWeather.insert_one({'datetime': historical_datetime,
                                                      'temperature': historical_dates_data[date]['temperature'],
                                                      'precipitation': historical_dates_data[date]['precipitation'],
                                                      'condition': historical_dates_data[date]['conditions']})

    return historical_dates_data


# retrieveForecastedWeatherData
# inputs: city name
# output: a json dataset of the data from the VisualCrossing's API containing a
#         city's forecasted weather in fahrenheit of the next 14 days. Also contains
#         the current day fyi. Weather conditions are also given.
def retrieve_forecasted_weather_data(city_name):
    forecasted_weather_call = FORECASTED_WEATHER_CALL.replace("[city_name]", city_name)
    try:
        response = requests.get(url=forecasted_weather_call)
    except:
        return response.reason
    days = response.json()['days']
    forecasts = {}
    for day in days[1:]:
        forecast = dict(temperature=day['temp'],
                        precipitation=day['precip'],
                        conditions=day['conditions']
                        )
        forecast_datetime = day['datetime']
        # This doesn't work with JSON, it want's a string as a key, not a datetime object
        # forecast_datetime = datetime.strptime(day['datetime'] + "T00:00:00Z", '%Y-%m-%dT%H:%M:%SZ')
        forecasts[forecast_datetime] = forecast

    return forecasts
