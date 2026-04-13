from django.urls import path
from . import views

urlpatterns = [
    path('ingest/', views.ingest_sensor_data, name='ingest'),
]
