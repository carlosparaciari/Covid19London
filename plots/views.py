from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

import io
import urllib
import base64
import numpy as np
from datetime import datetime
import matplotlib._color_data as mcd

from .plots_lib import increments, relative_cases_array, regions_trends, cumulative_cases, cumulative_plot_abs, cumulative_plot_rel, prepare_checklist_boroughs
from .models import Borough, Province, LondonDate, ItalyDate

def index(request):
	return HttpResponseRedirect(reverse('plots:cumulative_single', args=('London',)))

def cumul_abs(request,borough_name):

	context = cumulative_cases(request,LondonDate,Borough,borough_name)
	return render(request, 'plots/cumulative_abs.html', context)

def trends(request,borough_name):

	context = regions_trends(request,LondonDate,Borough,borough_name)
	return render(request, 'plots/trends.html', context)

def cumul_ita(request,province_name):

	context = cumulative_cases(request,ItalyDate,Province,province_name)
	return render(request, 'plots/cumulative_italy.html', context)

def trends_ita(request,province_name):

	context = regions_trends(request,ItalyDate,Province,province_name)
	return render(request, 'plots/trends_italy.html', context)

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
