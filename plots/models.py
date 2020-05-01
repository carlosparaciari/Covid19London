from django.contrib.postgres.fields import ArrayField
from django.db import models

from datetime import datetime

class Borough(models.Model):
    name = models.CharField(max_length=200)
    population = models.IntegerField(default=0)
    cumulative_array = ArrayField(models.IntegerField())

    def __str__(self):
        return self.name

class Dates(models.Model):
    dates_array = ArrayField(models.CharField(max_length=200))

    def get_dates(self):
    	return [datetime.strptime(date,'%d-%b-%Y') for date in self.dates_array]
