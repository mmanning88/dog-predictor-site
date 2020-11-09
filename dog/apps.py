from django.apps import AppConfig
from pathlib import Path
from django.conf import settings
from joblib import load


class DogConfig(AppConfig):
    name = 'dog'


# Main prediction algorithm to classify all dogs with a predicted outcome
# If model is updated than column transformer and bins maybe need to be updated as well
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
