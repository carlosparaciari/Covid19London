from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

import io
import urllib
import base64
import numpy as np
from datetime import datetime

from .plots_lib import increments, relative_cases_array, cumulative_plot_abs, cumulative_plot_rel, prepare_checklist_boroughs
from .models import Borough, Dates
from .forms import IncrementData

def index(request):
	return HttpResponseRedirect(reverse('plots:cumulative_single', args=('London',)))

def cumul_abs(request,borough_name):

	# Get dates array from database
	d = Dates.objects.get()
	obj_dates_array = d.get_dates()
	dates_array = np.array([obj_date.strftime('%d %b') for obj_date in obj_dates_array])

	# Get the latest date the database was updated
	last_update = obj_dates_array[-1]
	last_update_str = last_update.strftime('%d %B')

	# Get the date form (if it was filled)
	if request.method == 'POST':
		response_post = request.POST
		response_dict = response_post.dict()

		year_val = int(response_dict['date_year'])
		month_val = int(response_dict['date_month'])
		day_val = int(response_dict['date_day'])

		date_val = datetime(year_val, month_val, day_val)
		date_val_str = date_val.strftime('%d %b')

		if not date_val_str in dates_array:
			date_val = last_update
			date_val_str = date_val.strftime('%d %b')
	else:
		date_val = last_update
		date_val_str = date_val.strftime('%d %b')

	# Make the dropdown menu
	menu_items = [entry for entry in Borough.objects.values_list('name', flat=True)]

	# Get relevant borough and dates
	b = get_object_or_404(Borough, name__exact=borough_name)

	# Get the cumulative array and the daily increments for the borough
	b_cumulative_array = np.array(b.cumulative_array)
	b_increments = increments(b_cumulative_array)

	# Find cases for date requested
	date_val_str = date_val.strftime('%d %b')
	date_index = dates_array==date_val_str

	# Daily information
	daily_total = b_cumulative_array[date_index][0]
	daily_increment = b_increments[date_index][0]
	daily_percentage = "{:.1f}".format(100*daily_increment/(daily_total-daily_increment))

	# Plot of cumulative cases
	cumul_abs = cumulative_plot_abs(dates_array, b_cumulative_array, b_increments, b.name)

	# Save plot into buffer and convert to be able to visualise it
	buf = io.BytesIO()
	cumul_abs.savefig(buf,format='png')
	buf.seek(0)
	string = base64.b64encode(buf.read())
	uri = urllib.parse.quote(string)

	# Data to pass to the html page
	context = {}
	context['data']=uri
	context['items']=menu_items
	context['current']=b.name
	context['date']=last_update_str
	context['date_form'] = IncrementData(date_value=date_val) 
	context['daily_tot']=daily_total
	context['daily_inc']=daily_increment
	context['daily_per']=daily_percentage
	
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

	cumul_rel = cumulative_plot_rel(days_since,cases_pad_list,area_list)

	# Get the date of latest update
	d = Dates.objects.get()
	obj_dates_array = d.get_dates()
	last_update = obj_dates_array[-1]
	last_update_str = last_update.strftime('%d %B')

	# Save plot into buffer and convert to be able to visualise it
	buf = io.BytesIO()
	cumul_rel.savefig(buf,format='png')
	buf.seek(0)
	string = base64.b64encode(buf.read())
	uri = urllib.parse.quote(string)

	context = {'data':uri,
			   'items':checkbox_items,
			   'date':last_update_str
			  }

	return render(request, 'plots/cumulative_rel.html', context)
