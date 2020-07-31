from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

import io
import urllib
import base64
import numpy as np
from datetime import datetime
import matplotlib._color_data as mcd

from .plots_lib import increments, relative_cases_array, cumulative_plot_abs, cumulative_plot_rel, prepare_checklist_boroughs
from .models import Borough, LondonDate
from .forms import DailyCasesForm

def index(request):
	return HttpResponseRedirect(reverse('plots:cumulative_single', args=('London',)))

def cumul_abs(request,borough_name):

	# Get dates array from database and last date of update
	d = LondonDate.objects.get()
	dates_array = d.get_dates('%d %b')
	last_update = d.get_single_date_str(-1,'%d %B')

	# Set the date the user is interested in (default is latest day)
	date_val = d.get_single_date(-1)

	# If the user has provided a date
	if request.method == 'GET' and 'date' in request.GET:
		response = request.GET
		response_date = response.get('date')

		try:
			date_object = datetime.strptime(response_date, '%Y-%m-%d')
		except ValueError:
			pass
		else:
			date_requested = date_object.strftime('%d %b')
			if date_requested in dates_array:
				date_val = date_object

	date_val_str = date_val.strftime('%d %b')

	# Make the dropdown menu
	full_list = [entry for entry in Borough.objects.values_list('name', flat=True)]
	full_list.remove('London')
	sort_list = np.sort(full_list)
	menu_items = np.append(sort_list,'London')

	# Get relevant borough and dates
	b = get_object_or_404(Borough, name__exact=borough_name)

	# Get the cumulative array and the daily increments for the borough
	b_cumulative_array = np.array(b.cumulative_array)
	b_increments = increments(b_cumulative_array)

	# Find cases for date requested
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
	context['date']=last_update
	context['date_form']=DailyCasesForm(initial={'date': date_val}) 
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

	# Order the checkbox list
	checkbox_items.sort(key=lambda tup: tup[0])
	borough_list, bool_list = [*zip(*checkbox_items)]
	borough_array = np.array(borough_list)
	bool_array = np.array(bool_list)

	# Predefine colour palette
	col_array = np.array([col for n,col in enumerate(mcd.XKCD_COLORS.values()) if n < len(checkbox_items)])
	col_list = col_array[bool_array]

	# Make a list of the selected boroughs plus London
	area_list = borough_array[bool_array]
	area_list = np.append(area_list,'London')

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

	cumul_rel = cumulative_plot_rel(days_since,cases_pad_list,area_list,col_list)

	# Get the date of latest update
	d = LondonDate.objects.get()
	last_update = d.get_single_date_str(-1,'%d %B')

	# Save plot into buffer and convert to be able to visualise it
	buf = io.BytesIO()
	cumul_rel.savefig(buf,format='png')
	buf.seek(0)
	string = base64.b64encode(buf.read())
	uri = urllib.parse.quote(string)

	context = {}
	context['data']=uri
	context['items']=checkbox_items
	context['date']=last_update

	return render(request, 'plots/cumulative_rel.html', context)

def cumul_ita(request):
	
	return HttpResponse("Here it goes the Italian page.")

