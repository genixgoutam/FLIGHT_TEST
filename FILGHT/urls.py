"""
URL configuration for FILGHT project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views
# from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('optimize/', views.OptimizeView.as_view(), name='optimize'),
    path('choices/', views.choices_view, name='choices'),
    path('flight-info/', views.flight_info, name='flight_info'),
    # path('flight/', views.flight_view, name='flight'),
    path('map/', views.map_view, name='map'),
    path('api/airports/', views.AirportListView.as_view(), name='api-airports'),
    path('api/air_traffic/', views.api_air_traffic, name='api_air_traffic'),
    path('api/stops/', views.api_stops, name='api_stops'),
    path('api/all_airports/', views.api_all_airports, name='api_all_airports'),
    path('report/', views.report_view, name='report'),
    path('api/flights/', views.api_flights_json, name='api-flights'),
    path('api/flights/dynamic/', views.api_flights_dynamic, name='api-flights-dynamic'),
    path('api/report/', views.ReportDataView.as_view(), name='api-report'),
    path('api/init-supabase/', views.api_init_supabase, name='api-init-supabase'),
    
    # New API endpoints for fetching data by ID from Supabase
    path('api/air/<int:air_id>/', views.api_air_by_id, name='api-air-by-id'),
    path('api/weather/<int:weather_id>/', views.api_weather_by_id, name='api-weather-by-id'),
    path('api/fuel/<int:fuel_id>/', views.api_fuel_by_id, name='api-fuel-by-id'),
    path('api/safety/<int:safety_id>/', views.api_safety_by_id, name='api-safety-by-id'),
    path('api/flight/<int:flight_id>/', views.api_flight_by_id, name='api-flight-by-id'),
    
    # New API endpoints for api_flight.json data
    path('api/flight-data/air/<str:air_id>/', views.api_flight_by_air_id, name='api-flight-by-air-id'),
    path('api/flight-data/all/', views.api_all_flight_data, name='api-all-flight-data'),
    path('api/flight-data/condition/<str:condition>/', views.api_flight_by_condition, name='api-flight-by-condition'),
    path('api/flight-data/alert/<str:alert_status>/', views.api_flight_by_alert_status, name='api-flight-by-alert-status'),
    path('api/flight-data/air-ids/', views.api_available_air_ids, name='api-available-air-ids'),
    path('api/flight-data/conditions/', views.api_available_conditions, name='api-available-conditions'),
    path('api/flight-data/alert-statuses/', views.api_available_alert_statuses, name='api-available-alert-statuses'),
    path('api/flight-data/upload-to-supabase/', views.api_upload_flight_data_to_supabase, name='api-upload-flight-data-to-supabase'),
    path('api/flight-data/optimize/', views.api_flight_data_for_optimize, name='api-flight-data-for-optimize'),
    path('debug/api-flight-data/', views.debug_api_flight_data, name='debug-api-flight-data'),
    # path('test-report/', views.test_report_template, name='test-report'),

    # path('route/', views.optimize_view, name='route'),  # Remove duplicate
    # path('api/airports-json/', views.get_airports_json, name='get_airports_json'),

    path('chat-bot/', views.chat_bot, name='chat_bot'),
    #path('chat-bot/', chat_bot_view, name='chat_bot'), path('chat-bot/', views.chat_bot, name='chat_bot'),
    path('api/chat-gemini/', views.chat_gemini_api, name='chat_gemini_api'),
    path('api/ask-ai/', views.api_ask_ai, name='api_ask_ai'),

    # QAOA angle prediction API
    path('api/qaoa-predict/', views.QAOAPredictView.as_view(), name='api-qaoa-predict'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)      