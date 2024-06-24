# Do I Need an Umbrella? 
# An app that tells you if you need to bring umbrella before going outside
# Uses OpenWeather API to fetch weather data
# Daniel Kaijzer
# 06/23/2024

import requests
from datetime import datetime, timedelta
import re

# use OpenWeather API to fetch weather data
def get_weather_forecast(api_key, city):
    # Get latitude and longitude for the city
    geocoding_url = f'http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={api_key}'
    response = requests.get(geocoding_url)
    location_data = response.json()

    if response.status_code == 200 and location_data:
        latitude = location_data[0]['lat']
        longitude = location_data[0]['lon']
        
        # Get the weather forecast using the One Call API
        one_call_url = f'https://api.openweathermap.org/data/3.0/onecall?lat={latitude}&lon={longitude}&exclude=current,minutely,daily,alerts&units=metric&appid={api_key}'
        response = requests.get(one_call_url)
        if response.status_code == 200:
            return response.json()
        else:
            print("Error fetching the weather forecast data")
            print(response.status_code, response.text)
    else:
        print("Error fetching the location data")
        print(response.status_code, response.text)

    return None

# convert user input to time in 'YYYY-MM-DD HH' format
def convert_user_input(current_time, end_time_str):
    # Match patterns like "9 PM", "6:30 AM", "14:00", etc.
    match = re.match(r'(\d{1,2})(?::(\d{2}))?\s*(AM|PM|am|pm)?', end_time_str)
    if match:
        hour = int(match.group(1))
        minute = int(match.group(2) or 0)
        period = match.group(3)
        
        if period:
            period = period.upper()
            if period == 'PM' and hour != 12:
                hour += 12
            elif period == 'AM' and hour == 12:
                hour = 0
        
        end_time = current_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if end_time < current_time:
            end_time += timedelta(days=1)
        return end_time.strftime('%Y-%m-%d %H:%M')
    else:
        raise ValueError("Invalid time format")


# determines if user needs to bring umbrella
def should_bring_umbrella(api_key, city, end_time_str):
    # Get current time
    current_time = datetime.now()
    
    # Convert user input to proper end time in format 'YYYY-MM-DD HH'
    try:
        end_time_str = convert_user_input(current_time, end_time_str)
        end_time = datetime.strptime(end_time_str, '%Y-%m-%d %H:%M')
    except ValueError as e:
        print(e)
        return
    
    # Fetch weather forecast
    forecast_data = get_weather_forecast(api_key, city)
    
    # quit if weather data not fetched successfully
    if not forecast_data:
        return
    
    umbrella_needed = False
    weather_periods = []

    # Check hourly forecast
    for hour_data in forecast_data['hourly']:
        forecast_time = datetime.fromtimestamp(hour_data['dt'])
        if current_time <= forecast_time <= end_time:
            weather = hour_data['weather'][0]['main'].lower()
            if 'rain' in weather or 'snow' in weather or 'hail' in weather:
                umbrella_needed = True
                start_time = forecast_time.strftime('%Y-%m-%d %H:%M')
                end_time_period = (forecast_time + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M')
                weather_periods.append((start_time, end_time_period, weather))
    
    # Check the current weather
    current_weather = forecast_data['hourly'][0]['weather'][0]['main'].lower()
    if 'rain' in current_weather or 'snow' in current_weather or 'hail' in current_weather:
        umbrella_needed = True
        weather_periods.append(("now", "now", current_weather))

    if umbrella_needed:
        print("Yes, bring an umbrella.")
        for period in weather_periods:
            # if there is currently inclement weather
            if period[0] == "now":
                print(f"It is currently {period[2]}ing or about to rain.")
            else:
                print(f"It will {period[2]} from {period[0]} to {period[1]}.")
    else:
        print("You don't need an umbrella.")
        current_weather_description = forecast_data['hourly'][0]['weather'][0]['description']
        print(f"Current weather: {current_weather_description}")


# Replace 'your_api_key' with actual OpenWeatherMap API key
api_key = 'your_api_key'
city = 'New York' # can change to other city
end_time_str = input("Until what time will you be out for? (e.g., '9 PM', '6:30 AM'): ")

should_bring_umbrella(api_key, city, end_time_str)
