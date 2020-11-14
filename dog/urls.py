from django.urls import path
from . import views

urlpatterns = [

    path('', views.loginPage, name="login"),
    path('logout/', views.logoutUser, name="logout"),

    path('kennelselect/', views.kennelSelect, name="kennelSelect"),


    path('update/<str:pk>', views.updateDog, name="update"),
    path('remove/<str:pk>', views.removeDog, name="remove"),
    path('delete/<str:pk>', views.deleteDog, name="delete"),
    path('uploaddogs/<str:pk>', views.uploadDogs, name="uploadDogs"),
    path('downloaddogs/<str:pk>', views.downloadDogs, name="downloadDogs"),
    path('entry/<str:pk>', views.entry, name="entry"),

    path('kennel/genderplot/<str:pk>', views.genderPlot, name="genderPlot"),
    path('kennel/dayweekhm/<str:pk>', views.dayweekHeatMap, name="dayweekHeatMap"),
    path('kennel/outcomehm/<str:pk>', views.outcomeHeatMap, name="outcomeHeatMap"),
    path('kennel/outcometimeplot/<str:pk>', views.outcomeTimePlot, name="outcomeTimePlot"),
    path('kennel/outcomecompare', views.outcomeCompare, name="outcomeCompare"),

    path('<str:name>/home', views.kennelHome, name="kennelHome"),

]
