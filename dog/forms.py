from bootstrap_datepicker_plus import DateTimePickerInput
from django.forms import ModelForm, TextInput

from .models import Dog


class DogEntry(ModelForm):

    class Meta:
        model = Dog
        fields = [
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
            'created',
            'kennel'
        ]
        widgets = {
            'created': DateTimePickerInput(),
            'kennel': TextInput(attrs={'class': 'kennel'}),
        }

class RemoveDog(ModelForm):
    class Meta:
        model = Dog
        fields = [
            'true_outcome',
            'checkout'
        ]
        widgets = {
            'checkout': DateTimePickerInput(),
        }

    def __init__(self, *args, **kwargs):
        super(RemoveDog, self).__init__(*args, **kwargs)
        self.fields['checkout'].required = True
