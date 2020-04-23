from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
import io
import urllib, base64
import numpy as np
from .plots_lib import increments, relative_cases_array, cumulative_plot_abs, cumulative_plot_rel, prepare_checklist_boroughs
from .models import Borough, Dates

def index(request):
	return HttpResponseRedirect(reverse('plots:cumulative_single', args=('London',)))

def cumul_abs(request,borough_name):

	# Make the dropdown menu
	menu_items = [entry for entry in Borough.objects.values_list('name', flat=True)]

	# Get relevant borough and dates
	b = get_object_or_404(Borough, name__exact=borough_name)
	d = Dates.objects.get()

	# Get the dates and the date of latest update
	d_dates_array = np.array(d.dates_array)
	last_update = (d_dates_array)[-1]

	# Get the cumulative array and the daily increments for the borough
	b_cumulative_array = np.array(b.cumulative_array)
	b_increments = increments(b_cumulative_array)

	# Daily information
	daily_total = (b_cumulative_array)[-1]
	daily_increment = b_increments[-1]
	daily_percentage = "{:.1f}".format(100*daily_increment/(daily_total-daily_increment))

	# Plot of cumulative cases
	cumul_abs = cumulative_plot_abs(d_dates_array, b_cumulative_array, b_increments, b.name)

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
			   'daily_per':daily_percentage
			  }
	
	return render(request, 'plots/cumulative_abs.html', context)

def cumul_rel(request):

	# Prepare list of borough to be plotted
	if request.method == 'POST':
		response_post = request.POST
		response_dict = response_post.dict()

		borough_names = Borough.objects.values_list('name',flat=True)
		borough_names = borough_names.exclude(name='London')
		checkbox_items = [(name, name in response_dict) for name in borough_names]
	else:
		queryset_name_cases = Borough.objects.values_list('name','cumulative_array')
		queryset_name_cases = queryset_name_cases.exclude(name='London')
		checkbox_items = prepare_checklist_boroughs(queryset_name_cases)

	# Make a list of the selected boroughs plus London
	select_boroughs = lambda tup : tup[1]
	selected_boroughs = filter(select_boroughs,checkbox_items)
	area_list = [borough_name for borough_name,_ in selected_boroughs]
	area_list.append('London')

	# Extract the relative data for each borough, and only keep cases >= 1
	cases_rel_list = []
	length_arrays = []

	for borough_name in area_list:
		b = Borough.objects.get(name__exact=borough_name)
		cases_rel = relative_cases_array(b.cumulative_array, b.population)
		relevant_cases = cases_rel >= 1
		cases_rel_list.append(cases_rel[relevant_cases]) # Get the relevant cases
		length_arrays.append(np.sum(relevant_cases)) # Check the lenght of the above array

	# Compute the maximum length of the data when relative cases >= 1
	max_length = max(length_arrays)

	# Pad each array to get the same length
	cases_pad_list = []

	for cases_rel in cases_rel_list:
	    padding_length = max_length-cases_rel.size
	    pad_cumul_rel = np.pad(cases_rel, (0,padding_length), 'constant', constant_values=np.nan)
	    cases_pad_list.append(pad_cumul_rel)

	# Prepare the data to pass the plot function
	days_since = range(max_length) # Days since 1st relative case

	multiple_data = cases_pad_list[:-1]
	multiple_name = area_list[:-1]
	london_data = cases_pad_list[-1]

	cumul_rel = cumulative_plot_rel(days_since,multiple_data,multiple_name,london_data)

	# Get the date of latest update
	d = Dates.objects.get()
	last_update = (d.dates_array)[-1]

	# Save plot into buffer and convert to be able to visualise it
	buf = io.BytesIO()
	cumul_rel.savefig(buf,format='png')
	buf.seek(0)
	string = base64.b64encode(buf.read())
	uri = urllib.parse.quote(string)

	context = {'data':uri,
			   'items':checkbox_items,
			   'date':last_update
			  }

	return render(request, 'plots/cumulative_rel.html', context)
