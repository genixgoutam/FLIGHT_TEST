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
    path('map/', views.map_view, name='map'),
    path('api/airports/', views.AirportListView.as_view(), name='api-airports'),
    path('api/stops/', views.api_stops, name='api_stops'),
    path('api/all_airports/', views.api_all_airports, name='api_all_airports'),
    path('report/', views.report_view, name='report'),
    path('api/flights/', views.api_flights_json, name='api-flights'),
    path('api/flights/dynamic/', views.api_flights_dynamic, name='api-flights-dynamic'),
    path('api/report/', views.ReportDataView.as_view(), name='api-report'),
    
    path('chat-bot/', views.chat_bot, name='chat_bot'),
    path('api/chat-gemini/', views.chat_gemini_api, name='chat_gemini_api'),
    path('api/ask-ai/', views.api_ask_ai, name='api_ask_ai'),

    path('api/qaoa-predict/', views.QAOAPredictView.as_view(), name='api-qaoa-predict'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)      