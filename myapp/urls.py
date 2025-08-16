from django.urls import path
from .views import GPSDataListCreate
from django.urls import path
from .views import GPSDataListCreate, dashboard

urlpatterns = [
    path('api/gps-data/', GPSDataListCreate.as_view(), name='gps-data-list'),
    path('', dashboard, name='dashboard'),
]