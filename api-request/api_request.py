import requests
import os
from dotenv import load_dotenv


load_dotenv() #this is to read the .env content into the environment variables


api_key = os.getenv("WEATHERSTACK_API_KEY") 
api_url = f"http://api.weatherstack.com/current?access_key={api_key}&query=New York"

def fetch_data():
    print("Fetching Weather Data from WeatherStack API...")
    try:
        response = requests.get(api_url)
        response.raise_for_status() #this is a method from the request library that raises exceptions
        print("API Response Reseceived Successfully")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"An Error Occured: {e}")
        raise
# fetch_data()

# # print(response.json()) #a response of 200 means we're good
# # This is a mock data to avoid making too many API calls
# def mock_fetch_data():
#     return {'request': {'type': 'City', 'query': 'New York, United States of America', 'language': 'en', 'unit': 'm'}, 'location': {'name': 'New York', 'country': 'United States of America', 'region': 'New York', 'lat': '40.714', 'lon': '-74.006', 'timezone_id': 'America/New_York', 'localtime': '2025-09-11 23:10', 'localtime_epoch': 1757632200, 'utc_offset': '-4.0'}, 'current': {'observation_time': '03:10 AM', 'temperature': 21, 'weather_code': 113, 'weather_icons': ['https://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0008_clear_sky_night.png'], 'weather_descriptions': ['Clear '], 'astro': {'sunrise': '06:33 AM', 'sunset': '07:11 PM', 'moonrise': '09:08 PM', 'moonset': '11:14 AM', 'moon_phase': 'Waning Gibbous', 'moon_illumination': 86}, 'air_quality': {'co': '545.75', 'no2': '29.23', 'o3': '63', 'so2': '8.325', 'pm2_5': '15.725', 'pm10': '15.725', 'us-epa-index': '2', 'gb-defra-index': '2'}, 'wind_speed': 4, 'wind_degree': 24, 'wind_dir': 'NNE', 'pressure': 1021, 'precip': 0, 'humidity': 53, 'cloudcover': 0, 'feelslike': 21, 'uv_index': 0, 'visibility': 16, 'is_day': 'no'}}

# # print(mock_fetch_data())