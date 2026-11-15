from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('cars/', views.car_list, name='car_list'),
    path('cars/<int:pk>/', views.car_detail, name='car_detail'),
    path('booking/confirmation/<str:ref>/', views.booking_confirmation, name='booking_confirmation'),
    path('booking/lookup/', views.booking_lookup, name='booking_lookup'),
    path('booking/cancel/<str:ref>/', views.cancel_booking, name='cancel_booking'),
    path('about/', views.about, name='about'),
]
