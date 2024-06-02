from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),

    path('display/', views.display_stocks, name='display_stocks'),
    path('get_stock_data/', views.get_stock_data, name='get_stock_data'),

    path('floor-data/', views.display_floor, name='display_floor'),
    path('get_floor_data/', views.get_floor_data, name='get_floor_data'),
]

