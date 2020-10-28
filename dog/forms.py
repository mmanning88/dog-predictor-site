from django.forms import ModelForm
from bootstrap_datepicker_plus import DateTimePickerInput

from .models import Dog


class DogEntry(ModelForm):
    class Meta:
        model = Dog
        fields = [
            'kennel',
            'sex',
            'fixed',
            'breed',
            'condition',
            'intake_type',
            'coat_pattern',
            'primary_color',
            'age',
            'mixed',
            'puppy',
            'bully',
            'created'
        ]
        widgets = {
            'created': DateTimePickerInput(),
        }
        Dog.outcome = Dog.predictOutcome


class RemoveDog(ModelForm):
    class Meta:
        model = Dog
        fields = [
            'true_outcome'
        ]
