from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('game/', include('game.urls')),
    path('users/', include('users.urls')),
    path('', include('homepage.urls')),
]
