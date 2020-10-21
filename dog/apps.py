from django.apps import AppConfig
from pathlib import Path
from django.conf import settings
from joblib import load
import pandas as pd


class DogConfig(AppConfig):
    name = 'dog'


class PredictorConfig(AppConfig):

    path = Path.joinpath(settings.MODEL_URL, 'primary_model.pkl')

    with open(path, 'rb') as pickled:
        classifier = load(pickled)

    path = Path.joinpath(settings.MODEL_URL, 'primary_ct.pkl')

    with open(path, 'rb') as pickled:
        ct = load(pickled)

    path = Path.joinpath(settings.MODEL_URL, 'columns.pkl')

    with open(path, 'rb') as pickled:
        columns = load(pickled)

    path = Path.joinpath(settings.MODEL_URL, 'bins.pkl')

    with open(path, 'rb') as pickled:
        bins = load(pickled)

