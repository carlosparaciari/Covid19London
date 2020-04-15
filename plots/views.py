from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
import io
import urllib, base64
from .plots_lib import increments, cumulative_plot_abs
from .models import Borough, Dates

def index(request):
	return HttpResponseRedirect(reverse('plots:cumulative_single', args=('London',)))

def cumul_abs(request,borough_name):

	# Make the dropdown menu
	menu_items = [entry.name for entry in Borough.objects.all()]

	# Get relevant borough and dates
	b = get_object_or_404(Borough, name__exact=borough_name)
	d = Dates.objects.get()

	# Get the daily increments for the borough 
	b_increments = increments(b.cumulative_array)

	# Plot of cumulative cases
	cumul_abs = cumulative_plot_abs(d.dates_array, b.cumulative_array, b_increments, b.name)

	# Save plot into buffer and convert to be able to visualise it
	buf = io.BytesIO()
	cumul_abs.savefig(buf,format='png')
	buf.seek(0)
	string = base64.b64encode(buf.read())
	uri = urllib.parse.quote(string)

	context = {'data':uri,'items':menu_items, 'current':b.name}
	
	return render(request, 'plots/cumulative_abs.html', context)