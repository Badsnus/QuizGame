from django.urls import path, include

from . import views

app_name = 'users'

urlpatterns = [
    path('profile/', views.ProfileView.as_view(), name='profile'),

    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),

    path(
        'password/change/',
        views.CustomPasswordChangeView.as_view(),
        name='change_password'
    ),
    path(
        'password/change/done/',
        views.CustomPasswordChangeDoneView.as_view(),
        name='change_password_done'
    ),

    path('', include('django.contrib.auth.urls'))
]
