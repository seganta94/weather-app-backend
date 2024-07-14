import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
import pandas as pd
import logging

logger = logging.getLogger(__name__)

@api_view(['GET'])
def get_weather(request):
    latitude = request.GET.get('latitude')
    longitude = request.GET.get('longitude')
    logger.debug(f"Received request with latitude: {latitude} and longitude: {longitude}")

    if latitude and longitude:
        try:
            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude": float(latitude),
                "longitude": float(longitude),
                "daily": "apparent_temperature_max,apparent_temperature_min",
                "timezone": "GMT"
            }
            logger.debug(f"Making API request to {url} with params: {params}")
            response = requests.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            daily = data.get('daily', {})

            daily_data = {
                "time": daily.get('time', []),
                "apparent_temperature_max": daily.get('apparent_temperature_max', []),
                "apparent_temperature_min": daily.get('apparent_temperature_min', [])
            }

            # Filter data for today
            today_date = pd.to_datetime('today').strftime('%Y-%m-%d')
            today_data = {
                "time": [],
                "apparent_temperature_max": [],
                "apparent_temperature_min": []
            }

            for i, date in enumerate(daily_data['time']):
                if date == today_date:
                    today_data['time'].append(date)
                    today_data['apparent_temperature_max'].append(daily_data['apparent_temperature_max'][i])
                    today_data['apparent_temperature_min'].append(daily_data['apparent_temperature_min'][i])

            if not today_data['time']:
                return Response({"error": "No data available for today"}, status=404)

            daily_dataframe = pd.DataFrame(data=today_data)
            daily_data_json = daily_dataframe.to_json(orient='records', date_format='iso')

            logger.debug(f"Returning response: {daily_data_json}")
            return Response(daily_data_json, content_type='application/json')
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            return Response({"error": str(e)}, status=500)
    return Response({"error": "Latitude and longitude not provided"}, status=400)
