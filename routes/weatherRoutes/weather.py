from routes.authorization import requires_auth, AuthError, handle_auth_error
from flask_cors import cross_origin
from extensions import *
from dataIngestion import *

weatherRoutes = Blueprint('weatherRoutes', __name__)

# Error handler
weatherRoutes.register_error_handler(AuthError, handle_auth_error)

# Assign api_audience
weather_api_audience = os.environ.get('WEATHER_API_AUDIENCE')


# store_historical_weather
# GETs VisualCrossing's Weather API data and store it in our db
@weatherRoutes.route('/weather/historical/<string:city_name>', methods=['POST'])
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth(audience=weather_api_audience)
def store_historical_weather(city_name):
    # get the orders data from the users square account
    res = retrieve_historical_weather_data(city_name)

    return res


# get_forecasted_weather
# GETs and returns two weeks of forecasted weather data from VisualCrossing's Weather API
@weatherRoutes.route('/weather/forecast/<string:city_name>', methods=['GET'])
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth(audience=weather_api_audience)
def get_forecasted_weather(city_name):
    # get the orders data from the users square account
    res = retrieve_forecasted_weather_data(city_name)

    return res
