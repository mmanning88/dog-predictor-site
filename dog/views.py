from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from django_pandas.io import read_frame

import holoviews as hv


from .forms import DogEntry, RemoveDog
from .models import *
from .decorators import *


from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import ColumnDataSource
from bokeh.transform import jitter


# Create your views here.

@unauthenticated_user
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

@login_required(login_url='login')
def home(request):
    dogs = Dog.objects.all()
    for dog in dogs:
        if dog.pred_outcome == 'No Outcome':
            dog.pred_outcome = dog.predictOutcome
    kennels = Kennel.objects.all()

    context = {'dogs': dogs, 'kennels': kennels}

    return render(request, 'dog/home.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['operator'])
def entry(request):
    form = DogEntry()
    if request.method == 'POST':
        form = DogEntry(request.POST, instance=Dog())
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form': form}

    return render(request, 'dog/entry.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['operator'])
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

@login_required(login_url='login')
@allowed_users(allowed_roles=['operator'])
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

@login_required(login_url='login')
@allowed_users(allowed_roles=['operator'])
def deleteDog(request, pk):
    dog = Dog.objects.get(id=pk)

    context = {'dog': dog}

    if request.method == 'POST':
        dog.delete()
        return redirect('/')

    return render(request, 'dog/delete.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['operator'])
def kennel(request):
    kennels = Kennel.objects.all()


    context = {'kennels': kennels}

    return render(request, 'dog/kennel.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['operator'])
def dayweekHeatMap(request, pk):
    hv.extension('bokeh')
    kennel = Kennel.objects.get(id=pk)
    dogs = kennel.dog_set.all()

    data = read_frame(dogs, fieldnames=['day', 'hour'])
    data = data.groupby(["day", "hour"]).size().reset_index(name="counts")
    hm = hv.HeatMap(data).sort()
    hm.opts(xticks=None, colorbar=True, width=600, xlabel='Day', ylabel='Hour', tools=['hover'], title="Day And Week Heatmap for " + kennel.name)
    renderer = hv.renderer('bokeh')
    plot = renderer.get_plot(hm).state

    script, div = components(plot)

    context = {'script': script, 'div': div, 'kennel':kennel}
    return render(request, 'dog/dayweekhm.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['operator'])
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

    plot = figure(x_range=items, plot_height=600, plot_width=600, title="Outcomes By Sex for " + kennel.name,
                  toolbar_location="right", tools="wheel_zoom,box_zoom,reset, hover, save")
    plot.title.text_font_size = '20pt'

    plot.vbar_stack(sexes, x='items', width=0.9, color=colors, source=data, legend_label=sexes)

    script, div = components(plot)

    context = {'kennel': kennel, 'dogs': dogs, 'script': script, 'div': div}

    return render(request, 'dog/genderPlot.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['operator'])
def outcomeHeatMap(request, pk):
    hv.extension('bokeh')
    kennel = Kennel.objects.get(id=pk)
    dogs = kennel.dog_set.all()

    data = read_frame(dogs, fieldnames=['intake_type', 'pred_outcome'])
    data = data.groupby(["intake_type", "pred_outcome"]).size().reset_index(name="counts")
    hm = hv.HeatMap(data).sort()
    hm.opts(xticks=None, colorbar=True, width=600, xlabel='Intake Type', ylabel='Predicted Outcome',
            tools=['hover'], cmap='inferno', title="Outcomes by Intake Type for " + kennel.name)
    renderer = hv.renderer('bokeh')
    plot = renderer.get_plot(hm).state
    script, div = components(plot)

    context = {'script': script, 'div': div, 'kennel':kennel}
    return render(request, 'dog/outcomehm.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['operator'])
def outcomeTimePlot(request, pk):
    kennel = Kennel.objects.get(id=pk)
    dogs = kennel.dog_set.all()

    data = read_frame(dogs, fieldnames=['created', 'pred_outcome'])
    items = ["Adoption", "Transfer", "Euthanasia", "Return to Owner"]
    data['created'] = data['created'].dt.strftime('%H:%M')
    data['created'] = data['created'].astype('datetime64[ns]')
    source = ColumnDataSource(data)
    plot = figure(plot_width=800, plot_height=400, y_range=items, x_axis_type='datetime',
               title="Outcomes by Time and Day for " + kennel.name, tools='save')

    plot.circle(x='created', y=jitter('pred_outcome', width=0.6, range=plot.y_range), source=source, alpha=0.4)

    plot.xaxis[0].formatter.days = ['%Hh']
    plot.x_range.range_padding = 0
    plot.ygrid.grid_line_color = None

    script, div = components(plot)

    context = {'kennel': kennel, 'script': script, 'div': div}

    return render(request, 'dog/outcomeTimePlot.html', context)



@login_required(login_url='login')
@allowed_users(allowed_roles=['operator'])
def outcomeCompare(request):
    hv.extension('bokeh')
    kennel = Kennel.objects.get(id=2)
    dogs = kennel.dog_set.all()
    data = read_frame(dogs, fieldnames=['pred_outcome', 'true_outcome'])
    data = data.groupby(["pred_outcome", "true_outcome"]).size().reset_index(name="norm")
    a = data.groupby('pred_outcome')['norm'].transform('sum')
    data['norm'] = data['norm'].div(a)
    hm = hv.HeatMap(data).sort()
    hm.opts(colorbar=True, width=600, xlabel='Predicted Outcome', ylabel='True Outcome',
            cmap='inferno', normalize=True, tools=['hover'], title="Confusion Matrix for Historical Data")
    renderer = hv.renderer('bokeh')
    plot = renderer.get_plot(hm).state
    script, div = components(plot)

    context = {'script': script, 'div': div, 'kennel':kennel}
    return render(request, 'dog/outcomehm.html', context)

