from django.contrib.postgres.fields import ArrayField
from django.db import models

class Borough(models.Model):
    name = models.CharField(max_length=200)
    population = models.IntegerField(default=0)
    cumulative_array = ArrayField(models.IntegerField())

