from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout

import numpy as np
import pandas as pd
from django_pandas.io import read_frame
import holoviews as hv

from bootstrap_datepicker_plus import DateTimePickerInput

from .forms import DogEntry, RemoveDog
from .models import *

from django.shortcuts import render
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import HoverTool, LassoSelectTool, WheelZoomTool, PointDrawTool, ColumnDataSource, Select, \
    LinearColorMapper
from bokeh.palettes import Category20c, Spectral6, Spectral4
from bokeh.transform import cumsum, factor_cmap


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
    for dog in dogs:
        if dog.pred_outcome == 'No Outcome':
            dog.pred_outcome = dog.predictOutcome
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


def updateDog(request, pk):
    dog = Dog.objects.get(id=pk)
    form = DogEntry(instance=dog)

    context = {'form': form}

    if request.method == 'POST':
        form = DogEntry(request.POST, instance=dog)
        if form.is_valid():
            form.save()
            return redirect('/')

    return render(request, 'dog/entry.html', context)


def removeDog(request, pk):
    dog = Dog.objects.get(id=pk)
    kennels = Kennel.objects.all()
    form = RemoveDog(instance=dog)

    context = {'dog': dog, 'kennels': kennels, 'form': form}

    if request.method == 'POST':
        form = RemoveDog(request.POST, instance=dog)
        if form.is_valid():
            dog.kennel = kennels.get(name='Historical Outcomes')
            form.save()
            return redirect('/')

    return render(request, 'dog/remove.html', context)


def deleteDog(request, pk):
    dog = Dog.objects.get(id=pk)

    context = {'dog': dog}

    if request.method == 'POST':
        dog.delete()
        return redirect('/')

    return render(request, 'dog/delete.html', context)


def kennel(request):
    kennels = Kennel.objects.all()


    context = {'kennels': kennels}

    return render(request, 'dog/kennel.html', context)

def dayweekHeatMap(request, pk):
    hv.extension('bokeh')
    kennel = Kennel.objects.get(id=pk)
    dogs = kennel.dog_set.all()

    data = read_frame(dogs, fieldnames=['day', 'hour'])
    data = data.groupby(["day", "hour"]).size().reset_index(name="counts")
    hm = hv.HeatMap(data).sort()
    hm.opts(xticks=None, colorbar=True, width=600, xlabel='Day', ylabel='Hour')
    renderer = hv.renderer('bokeh')
    plot = renderer.get_plot(hm).state

    script, div = components(plot)

    context = {'script': script, 'div': div, 'kennel':kennel}
    return render(request, 'dog/dayweekhm.html', context)

def genderPlot(request, pk):
    kennel = Kennel.objects.get(id=pk)
    dogs = kennel.dog_set.all()
    sexes = ['male', 'female']
    adoptions_male = 0
    transfers_male = 0
    euthanasias_male = 0
    returns_male = 0
    adoptions_female = 0
    transfers_female = 0
    euthanasias_female = 0
    returns_female = 0
    colors = ["#add8e6", "#FFC0CB"]
    items = ["Adoption", "Transfer", "Euthanasia", "Return to Owner"]

    for dog in dogs:
        if dog.sex == 'Male':
            if 'Adoption' in dog.pred_outcome:
                adoptions_male += 1
            elif 'Transfer' in dog.pred_outcome:
                transfers_male += 1
            elif 'Euthanasia' in dog.pred_outcome:
                returns_male += 1
            elif 'Return to Owner' in dog.pred_outcome:
                euthanasias_male += 1
        if dog.sex == 'Female':
            if 'Adoption' in dog.pred_outcome:
                adoptions_female += 1
            elif 'Transfer' in dog.pred_outcome:
                transfers_female += 1
            elif 'Euthanasia' in dog.pred_outcome:
                returns_female += 1
            elif 'Return to Owner' in dog.pred_outcome:
                euthanasias_female += 1

    data = {
        'items': items,
        'male': [adoptions_male, transfers_male, euthanasias_male, returns_male],
        'female': [adoptions_female, transfers_female, euthanasias_female, returns_female]
    }

    plot = figure(x_range=items, plot_height=600, plot_width=600, title="Dog Outcomes By Sex",
                  toolbar_location="right", tools="pan,wheel_zoom,box_zoom,reset, hover, tap, crosshair")
    plot.title.text_font_size = '20pt'

    plot.vbar_stack(sexes, x='items', width=0.9, color=colors, source=data, legend_label=sexes)

    script, div = components(plot)

    context = {'kennel': kennel, 'dogs': dogs, 'script': script, 'div': div}

    return render(request, 'dog/genderPlot.html', context)

def outcomeHeatMap(request, pk):
    hv.extension('bokeh')
    kennel = Kennel.objects.get(id=pk)
    dogs = kennel.dog_set.all()

    data = read_frame(dogs, fieldnames=['intake_type', 'pred_outcome'])
    data = data.groupby(["intake_type", "pred_outcome"]).size().reset_index(name="counts")
    hm = hv.HeatMap(data).sort()
    hm.opts(xticks=None, colorbar=True, width=600, xlabel='Intake Type', ylabel='Predicted Outcome')
    renderer = hv.renderer('bokeh')
    plot = renderer.get_plot(hm).state
    script, div = components(plot)

    context = {'script': script, 'div': div, 'kennel':kennel}
    return render(request, 'dog/outcomehm.html', context)

def outcomeTimePlot(request, pk):
    kennel = Kennel.objects.get(id=pk)
    dogs = kennel.dog_set.all()



    script, div = components(plot)

    context = {'kennel': kennel, 'script': script, 'div': div}

    return render(request, 'dog/genderPlot.html', context)

