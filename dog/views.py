import io, csv
from math import pi

from bokeh.layouts import row
from bokeh.palettes import Category20c, Spectral4, brewer, d3
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from django.http import HttpResponseRedirect, JsonResponse

from django_pandas.io import read_frame

import holoviews as hv
from holoviews import opts

from .forms import DogEntry, RemoveDog
from .models import *
from .decorators import *

from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import ColumnDataSource
from bokeh.transform import jitter, cumsum, factor_cmap


# Create your views here.

@unauthenticated_user
def loginPage(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('kennelSelect')
        else:
            messages.info(request, "Username or password is incorrect")

    context = {}
    return render(request, 'dog/login.html', context)


def logoutUser(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def kennelSelect(request):
    kennels = Kennel.objects.all()

    context = {'kennels': kennels}
    return render(request, 'dog/kennelselect.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['operator'])
def kennelHome(request, name):
    kennel = Kennel.objects.get(name=name)
    dogs = kennel.dog_set.all()
    for dog in dogs:
        if dog.pred_outcome is None:
            dog.save()
    adoptions_p = 0
    transfers_p = 0
    euthanasias_p = 0
    returns_p = 0
    adoptions_t = 0
    transfers_t = 0
    euthanasias_t = 0
    returns_t = 0
    if dogs:
        for dog in dogs.iterator():
            if dog.pred_outcome == 'Adoption':
                adoptions_p += 1
            elif dog.pred_outcome == 'Transfer':
                transfers_p += 1
            elif dog.pred_outcome == 'Euthanasia':
                euthanasias_p += 1
            elif dog.pred_outcome == 'Return to Owner':
                returns_p += 1
            if kennel.id == 2:
                if dog.true_outcome == 'Adoption':
                    adoptions_t += 1
                elif dog.true_outcome == 'Transfer':
                    transfers_t += 1
                elif dog.true_outcome == 'Euthanasia':
                    euthanasias_t += 1
                elif dog.true_outcome == 'Return to Owner':
                    returns_t += 1

    x = {
        'Adoption': adoptions_p,
        'Transfer': transfers_p,
        'Euthanasia': euthanasias_p,
        'Return to Owner': returns_p,
    }

    data = pd.Series(x).reset_index(name='value').rename(columns={'index': 'outcome'})
    data['angle'] = data['value'] / data['value'].sum() * 2 * pi
    data['color'] = Category20c[len(x)]

    plot = figure(plot_height=350, plot_width=400, title="Total Number of Predicted Outcomes for Kennel",
                  toolbar_location=None,
                  tools="hover", tooltips="@outcome: @value", x_range=(-0.5, 1.0))

    plot.wedge(x=0, y=1, radius=0.4,
               start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
               line_color="white", fill_color='color', legend_field='outcome', source=data)

    plot.axis.axis_label = None
    plot.axis.visible = False
    plot.grid.grid_line_color = None

    # True outcome plot only created when kennel is historical outcomes
    if kennel.id == 2:
        x2 = {
            'Adoption': adoptions_t,
            'Transfer': transfers_t,
            'Euthanasia': euthanasias_t,
            'Return to Owner': returns_t,
        }

        data = pd.Series(x2).reset_index(name='value').rename(columns={'index': 'outcome'})
        data['angle'] = data['value'] / data['value'].sum() * 2 * pi
        data['color'] = Category20c[len(x)]

        plot2 = figure(plot_height=350, plot_width=400, title="Total Number of True Outcomes for Kennel",
                       toolbar_location=None,
                       tools="hover", tooltips="@outcome: @value", x_range=(-0.5, 1.0))

        plot2.wedge(x=0, y=1, radius=0.4,
                    start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
                    line_color="white", fill_color='color', legend_field='outcome', source=data)

        plot2.axis.axis_label = None
        plot2.axis.visible = False
        plot2.grid.grid_line_color = None

    if kennel.id == 2:
        script, div = components(row(plot, plot2))
    else:
        script, div = components(plot)
    context = {'dogs': dogs, 'kennel': kennel, 'script': script, 'div': div, }

    return render(request, 'dog/kennelhome.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['operator'])
def uploadDogs(request, pk):
    kennel = Kennel.objects.get(id=pk)

    context = {'kennel': kennel}

    if request.method == 'GET':
        return render(request, 'dog/uploaddogs.html', context)

    paramFile = io.TextIOWrapper(request.FILES['dogfile'].file)
    df = pd.read_csv(paramFile)
    row_iter = df.iterrows()

    objs = [
        Dog(
            sex=row['sex'],
            fixed=row['fixed'],
            breed=row['breed'],
            condition=row['condition'],
            intake_type=row['intake_type'],
            coat_pattern=row['coat_pattern'],
            primary_color=row['primary_color'],
            age=row['age'],
            mixed=row['mixed'],
            puppy=row['puppy'],
            bully=row['bully'],
            kennel=kennel
        )
        for index, row in row_iter
    ]

    try:
        msg = Dog.objects.bulk_create(objs)
        print('imported successfully')
    except Exception as e:
        print('Error While Importing Data: ', e)

    context = {'kennel': kennel}

    return render(request, 'dog/uploaddogs.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['operator'])
def downloadDogs(request, pk):
    kennel = Kennel.objects.get(pk=pk)
    dogs = kennel.dog_set.all()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="file.csv"'
    fields = ['id','sex','breed', 'condition','intake_type','coat_pattern','primary_color',
              'age','mixed','puppy','bully','kennel', 'pred_outcome', 'true_outcome']
    print(fields)
    writer = csv.DictWriter(response, fieldnames=fields)
    writer.writeheader()
    for dog in dogs:
        writer.writerow(
            {
                'id': dog.id,
                'sex': dog.sex,
                'breed': dog.breed,
                'condition': dog.condition,
                'intake_type': dog.intake_type,
                'coat_pattern': dog.coat_pattern,
                'primary_color': dog.primary_color,
                'age': dog.age,
                'mixed': dog.mixed,
                'puppy': dog.puppy,
                'bully': dog.bully,
                'kennel': dog.kennel.name,
                'pred_outcome': dog.pred_outcome,
                'true_outcome': dog.true_outcome
            }
        )

    return response

@login_required(login_url='login')
@allowed_users(allowed_roles=['operator'])
def entry(request, pk):
    kennel = Kennel.objects.get(id=pk)
    form = DogEntry(initial={'kennel':kennel})
    if request.method == 'POST':
        form = DogEntry(request.POST, instance=Dog())
        if form.is_valid():
            kennel_name = kennel.name
            form.save()
            return redirect('kennelHome', name=kennel_name)

    context = {'form': form, 'kennel': kennel}

    return render(request, 'dog/entry.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['operator'])
def updateDog(request, pk):
    dog = Dog.objects.get(id=pk)
    kennel = dog.kennel
    form = DogEntry(instance=dog)

    context = {'form': form, 'kennel': kennel}

    if request.method == 'POST':
        form = DogEntry(request.POST, instance=dog)
        if form.is_valid():
            kennelName = dog.kennel.name
            form.save()
            return redirect('kennelHome', name=kennelName)

    return render(request, 'dog/entry.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['operator'])
def removeDog(request, pk):
    dog = Dog.objects.get(id=pk)
    kennels = Kennel.objects.all()
    form = RemoveDog(instance=dog)
    kennelName = dog.kennel.name
    context = {'dog': dog, 'kennels': kennels, 'form': form}

    if request.method == 'POST':
        form = RemoveDog(request.POST, instance=dog)
        if form.is_valid():
            dog.kennel = kennels.get(name='Historical Outcomes')
            form.save()
            return redirect('kennelHome', name=kennelName)

    return render(request, 'dog/remove.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['operator'])
def deleteDog(request, pk):
    dog = Dog.objects.get(id=pk)
    kennel = dog.kennel

    context = {'dog': dog, 'kennel': kennel}

    if request.method == 'POST':
        kennelName = dog.kennel.name
        dog.delete()
        return redirect('kennelHome', name=kennelName)

    return render(request, 'dog/delete.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['operator'])
def dayweekHeatMap(request, pk):
    hv.extension('bokeh')
    kennel = Kennel.objects.get(id=pk)
    dogs = kennel.dog_set.all()

    data = read_frame(dogs, fieldnames=['day', 'hour'])
    data = data.groupby(["day", "hour"]).size().reset_index(name="counts")
    hm = hv.HeatMap(data).sort()
    hm.opts(xticks=None, colorbar=True, width=600, xlabel='Day', ylabel='Hour', tools=['hover'],
            title="Day And Week Heatmap for " + kennel.name)
    renderer = hv.renderer('bokeh')
    plot = renderer.get_plot(hm).state

    script, div = components(plot)

    context = {'script': script, 'div': div, 'kennel': kennel}
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

    return render(request, 'dog/genderplot.html', context)


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
    # hm = hm * hv.Labels(hm)
    renderer = hv.renderer('bokeh')
    plot = renderer.get_plot(hm).state
    script, div = components(plot)

    context = {'script': script, 'div': div, 'kennel': kennel}
    return render(request, 'dog/outcomehm.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['operator'])
def outcomeTimePlot(request, pk):
    kennel = Kennel.objects.get(id=pk)

    dogs = kennel.dog_set.all()
    kennel_string = 'true_outcome'
    if kennel.id != 2:
        kennel_string = 'pred_outcome'

    # Extract Hour and Minutes from creation date and set type as datetime
    data = read_frame(dogs, fieldnames=['created', kennel_string])
    items = ["Adoption", "Transfer", "Euthanasia", "Return to Owner"]
    data['created'] = data['created'].dt.strftime('%H:%M')
    data['created'] = data['created'].astype('datetime64[ns]')

    source = ColumnDataSource(data)
    plot = figure(plot_width=800, plot_height=350, y_range=items, x_axis_type='datetime',
                  title="Outcomes by Time and Day for " + kennel.name, tools='save, hover')

    plot.circle(x='created', y=jitter(kennel_string, width=0.7, range=plot.y_range), fill_color="navy", source=source,
                alpha=0.4)

    plot.xaxis[0].formatter.days = ['%Hh']
    plot.x_range.range_padding = 0
    plot.ygrid.grid_line_color = None

    script, div = components(plot)

    context = {'kennel': kennel, 'script': script, 'div': div}

    return render(request, 'dog/outcometimeplot.html', context)


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
            cmap='RdBu', normalize=True, tools=['hover'], title="Confusion Matrix for Historical Data")
    hm = hm * hv.Labels(hm)
    renderer = hv.renderer('bokeh')
    plot = renderer.get_plot(hm).state
    script, div = components(plot)

    context = {'script': script, 'div': div, 'kennel': kennel}
    return render(request, 'dog/outcomehm.html', context)
