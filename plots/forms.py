from django import forms
from django.forms import ModelForm

from .models import DateCases

from datetime import date

class DateInput(forms.DateInput):
	input_type = 'date'

class DailyCasesForm(ModelForm):

	class Meta:
		model = DateCases
		fields = ['date']
		widgets = {
		    'date': DateInput(),
		}
