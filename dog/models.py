from django.db import models
from django.core.validators import MaxValueValidator
from django.db.models.functions import datetime
from django.db.models.functions import ExtractDay, ExtractHour, ExtractMonth, ExtractYear
from datetime import datetime as dt


# Create your models here.

class Kennel(models.Model):
    name = models.CharField(max_length=200, null=True, unique=True)

    def __str__(self):
        return self.name


class Outcome(models.Model):
    name = models.CharField(max_length=30, null=True)

    def __str__(self):
        return self.name


class Dog(models.Model):
    SEX = (
        ('Male', 'M'),
        ('Female', 'F')
    )
    sex = models.CharField(max_length=10, choices=SEX, null=False)
    fixed = models.BooleanField(null=False)
    created = models.DateTimeField(null=False, default=dt.now)

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
        ('normal', 'Normal'),
        ('injured', 'Injured'),
        ('sick', 'Sick'),
        ('nursing', 'Nursing'),
        ('aged', 'Aged'),
        ('pregnant', 'Pregnant')
    )

    TYPES = (
        ('stray', 'Stray'),
        ('owner surrender', 'Owner Surrender'),
        ('public assist', 'Public Assist'),
        ('euthanasia request', 'Euthanasia Request')
    )

    COLORS = (
        ('none', 'None'),
        ('black', 'Black'),
        ('brown', 'Brown'),
        ('white', 'White'),
        ('blue ', 'Blue'),
        ('tan', 'Tan'),
        ('yellow', 'Yellow'),
        ('cream', 'Red'),
        ('tricolor', 'Tricolor'),
        ('merle', 'Merle'),
        ('sable', 'Sable'),
        ('tick', 'Tick'),
        ('brindle', 'Brindle')
    )

    breed = models.CharField(null=False, max_length=100, default='American Bulldog')
    condition = models.CharField(max_length=32, choices=CONDITIONS, null=False, default='normal')
    intake_type = models.CharField(max_length=100, choices=TYPES, null=False, default='stray')
    coat_pattern = models.CharField(max_length=32, choices=PATTERNS, null=False, default='none')
    primary_color = models.CharField(max_length=32, choices=COLORS, null=False, default='none')
    age = models.IntegerField(validators=[MaxValueValidator(20)])
    mixed = models.BooleanField(null=False, default=False)
    puppy = models.BooleanField(null=False, default=False)
    bully = models.BooleanField(null=False, default=False)
    outcome = models.ManyToManyField(Outcome, null=True, editable=True, blank=True)
    kennel = models.ForeignKey(Kennel, to_field='name', default='Default', on_delete=models.CASCADE)

    def getHour(self):
        return self.created.hour

    def getDay(self):
        return self.created.day

    def getMonth(self):
        return self.created.month

    def getYear(self):
        return self.created.year

    def getTimeInShelter(self):
        delta = dt.now().date() - self.created
        return delta

    def __str__(self):
        return str(self.age) + ' year old ' + self.breed
