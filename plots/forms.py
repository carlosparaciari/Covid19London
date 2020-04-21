from django import forms

class BoroughChecklist(forms.Form):
    show_borough = forms.BooleanField()