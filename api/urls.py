from django.urls import path
from .views import get_weather, get_location

urlpatterns = [
    path('weather', get_weather),
    path('location', get_location),
]
