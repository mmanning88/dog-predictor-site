from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout

from bootstrap_datepicker_plus import DateTimePickerInput

from .forms import DogEntry, RemoveDog
from .models import *

from django.shortcuts import render
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import HoverTool, LassoSelectTool, WheelZoomTool, PointDrawTool, ColumnDataSource
from bokeh.palettes import Category20c, Spectral6
from bokeh.transform import cumsum


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
        if dog.pred_outcome is 'No Outcome':
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


def kennel(request, pk):
    kennel = Kennel.objects.get(id=pk)
    dogs = kennel.dog_set.all()

    adoptions = 0
    transfers = 0
    euthanasias = 0
    returns = 0
    counts = []
    items = ["Adoption", "Transfer", "Euthanasia", "Return to Owner"]
    # for dog in dogs:
        # if 'Adoption' in dog.pred_outcome:
        #     adoptions += 1
    #     elif 'Transfer' in dog.values():
    #         transfers += 1
    #     elif 'Euthanasia' in dog.values():
    #         returns += 1
    #     elif 'Return to Owner' in dog.values():
    #         euthanasias += 1
    counts.extend([adoptions, transfers, euthanasias, returns])

    plot = figure(x_range=items, plot_height=600, plot_width=600, title="Dog Outcomes",
                  toolbar_location="right", tools="pan,wheel_zoom,box_zoom,reset, hover, tap, crosshair")
    plot.title.text_font_size = '20pt'

    plot.xaxis.major_label_text_font_size = "14pt"
    plot.vbar(items, top=counts, width=.4, color="firebrick", legend_label="Outcome Counts")
    plot.legend.label_text_font_size = '14pt'

    script, div = components(plot)

    context = {'kennel': kennel, 'dogs': dogs, 'script': script, 'div': div}

    return render(request, 'dog/kennel.html', context)
