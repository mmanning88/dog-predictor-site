from django.urls import path
from . import views

urlpatterns = [

    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutUser, name="logout"),

    path('entry/', views.entry, name="entry"),
    path('update/<str:pk>', views.updateDog, name="update"),
    path('remove/<str:pk>', views.removeDog, name="remove"),
    path('delete/<str:pk>', views.deleteDog, name="delete"),
    path('kennel/<str:pk>', views.kennel, name="kennel"),

    path('', views.home, name="home"),

]
