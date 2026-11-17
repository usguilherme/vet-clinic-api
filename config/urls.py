from django.contrib import admin
from django.urls import path
from core.views import fn_home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', fn_home),
]