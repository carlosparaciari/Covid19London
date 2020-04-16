from django.http import HttpResponseRedirect, HttpResponse
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
	menu_items = [entry for entry in Borough.objects.values_list('name', flat=True)]

	# Get relevant borough and dates
	b = get_object_or_404(Borough, name__exact=borough_name)
	d = Dates.objects.get()

	# Get the date of the latest update
	last_update = (d.dates_array)[-1]

	# Get the daily increments for the borough 
	b_increments = increments(b.cumulative_array)

	# Daily information
	daily_total = (b.cumulative_array)[-1]
	daily_increment = b_increments[-1]
	daily_percentage = "{:.1f}".format(100*daily_increment/(daily_total-daily_increment))

	# Prepare the list of the three most affected borough
	affected_boroughs = [(name,cases[-1]) for name,cases in Borough.objects.values_list('name','cumulative_array')]
	most_affected_boroughs = sorted(affected_boroughs, key=lambda tup: tup[1],reverse = True)
	main_boroughs = '+'.join([str(most_affected_boroughs[i][0]) for i in range(1,4)])

	# Plot of cumulative cases
	cumul_abs = cumulative_plot_abs(d.dates_array, b.cumulative_array, b_increments, b.name)

	# Save plot into buffer and convert to be able to visualise it
	buf = io.BytesIO()
	cumul_abs.savefig(buf,format='png')
	buf.seek(0)
	string = base64.b64encode(buf.read())
	uri = urllib.parse.quote(string)

	# Data to pass to the html page
	context = {'data':uri,
			   'items':menu_items,
			   'current':b.name,
			   'date':last_update,
			   'daily_tot':daily_total,
			   'daily_inc':daily_increment,
			   'daily_per':daily_percentage,
			   'blist':main_boroughs
			  }
	
	return render(request, 'plots/cumulative_abs.html', context)

def cumul_rel(request,borough_list):

	return HttpResponse('Dummy page for the relative plots!')