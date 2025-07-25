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
    path('api/all_ airports/', views.api_airports, name='api_airports'),
    path('', views.home, name='home'),
    path('optimize/', views.OptimizeView.as_view(), name='optimize'),
    path('choices/', views.choices_view, name='choices'),
    path('map/', views.map_view, name='map'),
    path('turbulence/', views.turbulence, name='turbulence'),
    path('api/stops/', views.api_stops, name='api_stops'),
    path('api/all_airports/', views.api_all_airports, name='api_all_airports'),
    path('report/', views.report, name='Report'),
    path('api/full-report/', views.full_report, name='full_report'),

    path('chat-bot/', views.chat_bot, name='chat_bot'),
    path('api/chat-gemini/', views.chat_gemini_api, name='chat_gemini_api'),
    path('api/ask-ai/', views.api_ask_ai, name='api_ask_ai'),

    path('api/qaoa-predict/', views.QAOAPredictView.as_view(), name='api-qaoa-predict'),
    path('api/flights/', views.api_flights, name='api_flights'),
    path('api/flight/', views.api_flights, name='api_flight'),
]
