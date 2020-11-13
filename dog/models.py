from django.db import models
from django.core.validators import MaxValueValidator
import pandas as pd
import numpy as np
from django.utils import timezone
from .apps import PredictorConfig

from calendar import day_name


# Create your models here.

class Kennel(models.Model):
    name = models.CharField(max_length=200, null=True, unique=True)

    def toDataFrame(self):
        pass


    def __str__(self):
        return str(self.id) + ' ' + self.name


class Outcome(models.Model):
    name = models.CharField(max_length=30, null=True)

    def __str__(self):
        return self.name


class Dog(models.Model):
    SEX = (
        ('Male', 'Male'),
        ('Female', 'Female')
    )
    sex = models.CharField(max_length=10, choices=SEX, null=False)
    fixed = models.BooleanField(null=False)
    created = models.DateTimeField(null=False, default=timezone.now, verbose_name="Intake Time (MM/DD/YYYY HH:MM)")
    checkout = models.DateTimeField(null=True, blank=True)

    PATTERNS = (
        ('none', 'None'),
        ('tricolor', 'Tricolor'),
        ('bicolor', 'Bicolor'),
        ('merle', 'Merle'),
        ('sable', 'Sable'),
        ('tick', 'Tick'),
        ('brindle', 'Brindle')
    )

    CONDITIONS = (
        ('Normal', 'Normal'),
        ('Injured', 'Injured'),
        ('Sick', 'Sick'),
        ('Nursing', 'Nursing'),
        ('Aggressive', 'Aggressive'),
        ('Aged', 'Aged'),
        ('Pregnant', 'Pregnant')
    )

    TYPES = (
        ('Stray', 'Stray'),
        ('Owner Surrender', 'Owner Surrender'),
        ('Public Assist', 'Public Assist'),
        ('Euthanasia Request', 'Euthanasia Request')
    )

    COLORS = (
        ('none', 'None'),
        ('black', 'Black'),
        ('brown', 'Brown'),
        ('white', 'White'),
        ('blue ', 'Blue'),
        ('red ', 'Red'),
        ('tan', 'Tan'),
        ('yellow', 'Yellow'),
        ('cream', 'Red'),
        ('gray', 'Gray'),
        ('orange', 'Orange'),
        ('buff', 'Buff'),
        ('gold', 'Gold'),
        ('silver', 'Silver')
    )

    OUTCOMES = (
        ('Adoption', 'Adoption'),
        ('Return to Owner', 'Return to Owner'),
        ('Transfer', 'Transfer'),
        ('Euthanasia', 'Euthanasia')
    )

    breed = models.CharField(null=False, max_length=100, default='American Bulldog')
    condition = models.CharField(max_length=40, choices=CONDITIONS, null=False, default='normal',
                                 verbose_name='intake condition')
    intake_type = models.CharField(max_length=100, choices=TYPES, null=False, default='stray')
    coat_pattern = models.CharField(max_length=32, choices=PATTERNS, null=False, default='none')
    primary_color = models.CharField(max_length=32, choices=COLORS, null=False, default='none')
    age = models.PositiveIntegerField(validators=[MaxValueValidator(20)], verbose_name="Age (0 for less than one year old)")
    mixed = models.BooleanField(null=False, default=False)
    puppy = models.BooleanField(null=False, default=False)
    bully = models.BooleanField(null=False, default=False, verbose_name='is this a bully breed?')
    kennel = models.ForeignKey(Kennel, default=1, null=True, on_delete=models.CASCADE)


    def getHour(self):
        return self.created.hour

    def getDay(self):
        return day_name[self.created.weekday()]

    def getMonth(self):
        return self.created.month

    bins = PredictorConfig.bins

    def getTimeInShelter(self):

        result = ((timezone.now() - self.created).seconds / 60) / 24
        return result

    # Dog objects can only be read by predictor as a list of lists
    # [['Female', 'Yes', 'Mixed', '(0.21, 1.04]', 'yellow', 14, 'Thursday', 12,
    #              '(7.5, 10.0]', 'Sick', 'Stray', 'Dog', 'Not Bully']]

    def returnList(Dog):
        hour = Dog.getHour()
        weekday = Dog.getDay()
        month = Dog.getMonth()
        days = Dog.getTimeInShelter()

        if Dog.bully:
            bully = 'Bully'
        else:
            bully = 'Not Bully'

        if Dog.fixed:
            fixed = 'Yes'
        else:
            fixed = 'No'

        if Dog.mixed:
            mixed = 'Mixed'
        else:
            mixed = 'Purebred'

        if Dog.coat_pattern == 'None':
            coat = Dog.primary_color
        elif Dog.primary_color == 'None':
            coat = Dog.coat_pattern
        else:
            coat = Dog.primary_color

        if Dog.puppy:
            puppy = 'Puppy'
        else:
            puppy = 'Dog'
        dog_entry = [[Dog.sex, fixed, mixed, days, coat, hour,
                      weekday, month, Dog.age, Dog.condition, Dog.intake_type,
                      puppy, bully]]
        return dog_entry

    def toDataframe(Dog):
        df = Dog.returnList()
        df = pd.DataFrame(df, columns=PredictorConfig.columns)
        df['time_in_shelter_days_12'] = pd.cut(df['time_in_shelter_days_12'], bins=PredictorConfig.bins)
        for col in df:
            df[col] = df[col].astype('category')
        df = PredictorConfig.ct.transform(df)
        return df

    def predictOutcome(self):
        result = PredictorConfig.classifier.predict(self.toDataframe())
        if result == [0]:
            result = 'Return to Owner'
        elif result == [1]:
            result = 'Transfer'
        elif result == [2]:
            result = 'Adoption'
        elif result == [3]:
            result = 'Euthanasia'
        return result

    pred_outcome = models.CharField(max_length=50, editable=True, null=True)
    true_outcome = models.CharField(max_length=50, choices=OUTCOMES, null=True, editable=True, blank=True)
    hour = models.IntegerField(null=False, default=0)
    day = models.CharField(null=False, default='Sunday', max_length=20)

    def __str__(self):
        return 'ID: ' + str(self.id) + ' ' + self.breed

    def save(self, *args, **kwargs):
        self.pred_outcome = self.predictOutcome()
        self.hour = self.getHour()
        self.day = self.getDay()

        super(Dog, self).save(*args, **kwargs)

