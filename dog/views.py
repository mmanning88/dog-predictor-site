import joblib
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout

from bootstrap_datepicker_plus import DateTimePickerInput

from .forms import DogEntry
from .models import *

# Create your views here.

def loginPage(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request, "Username or password is incorrect")

    context = {}
    return render(request, 'dog/login.html', context)


def logoutUser(request):
    logout(request)
    return redirect('login')


def home(request):
    dogs = Dog.objects.all()
    kennels = Kennel.objects.all()

    context = {'dogs': dogs, 'kennels': kennels}

    return render(request, 'dog/home.html', context)


def entry(request):
    form = DogEntry()
    if request.method == 'POST':
        form = DogEntry(request.POST, instance=Dog())
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form': form}

    return render(request, 'dog/entry.html', context)


def shelter(request):
    context = {}

    return render(request, 'dog/shelter.html', context)

