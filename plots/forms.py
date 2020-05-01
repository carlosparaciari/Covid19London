from django import forms

from datetime import date

class BoroughChecklist(forms.Form):
	show_borough = forms.BooleanField()

class IncrementData(forms.Form):

	date = forms.DateField(widget = forms.SelectDateWidget( years=(2020,) ))

	def __init__(self,*args,**kwargs):

		try:
			self.date_init = kwargs.pop('date_value')
		except KeyError:
			self.date_init = date.today()

		super(IncrementData,self).__init__(*args,**kwargs)

		self.fields['date'].initial = self.date_init
