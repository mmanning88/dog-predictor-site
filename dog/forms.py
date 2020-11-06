from django.forms import ModelForm, Form, CharField, Select, ChoiceField
from bootstrap_datepicker_plus import DateTimePickerInput

from .models import Dog, Kennel


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
        ]
        widgets = {
            'created': DateTimePickerInput(),
        }

class RemoveDog(ModelForm):
    class Meta:
        model = Dog
        fields = [
            'true_outcome'
        ]

