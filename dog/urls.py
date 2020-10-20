from django.urls import path
from . import views

urlpatterns = [

    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutUser, name="logout"),

    path('entry/', views.entry, name="entry"),
    path('shelter/', views.shelter, name="shelter"),

    path('', views.home, name="home"),

]
