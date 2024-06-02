from django.contrib import admin
from django.urls import path, include
from django_distill import distill_path

urlpatterns = [
    distill_path('admin/', admin.site.urls),
    distill_path('', include('stocks.urls')),
]



# from django.contrib import admin
# from django.urls import path, include

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('', include('stocks.urls')),
# ]

