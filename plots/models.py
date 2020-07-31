from django.contrib.postgres.fields import ArrayField
from django.db import models

from datetime import datetime
import numpy as np

# Abstract model for data of regional areas
class RegionalArea(models.Model):
	name = models.CharField(max_length=200)
	population = models.IntegerField(default=0)
	cumulative_array = ArrayField(models.IntegerField())

	def __str__(self):
		return self.name

	class Meta:
        abstract = True

# Model for saving cumulative cases of London's boroughs
class Borough(RegionalArea):

	class Meta(RegionalArea.Meta):
        db_table = 'London_boroughs'

# Model for saving cumulative cases of Italian province
class Province(RegionalArea):

	class Meta(RegionalArea.Meta):
        db_table = 'Italy_provinces'

# Model to save the dates since first infection
class Dates(models.Model):
	dates_array = ArrayField(models.CharField(max_length=200))

	def get_dates(self,date_format):
		date_object_array = [datetime.strptime(date,'%d-%b-%Y') for date in self.dates_array]
		return np.array([date_object.strftime(date_format) for date_object in date_object_array])

	def get_single_date(self,index):
		date_object_array = [datetime.strptime(date,'%d-%b-%Y') for date in self.dates_array]
		size_array = len(date_object_array)

		if (index >= size_array) or (index <= -size_array-1):
			raise IndexError

		return date_object_array[index]

	def get_single_date_str(self,index,date_format):
		date_object = self.get_single_date(index)
		return date_object.strftime(date_format)

# Model to collect user data requests
class DateCases(models.Model):
	date = models.DateField()