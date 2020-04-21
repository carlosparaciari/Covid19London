from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
import io
import urllib, base64
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

	# Get the date of the latest update
	last_update = (d.dates_array)[-1]

	# Get the daily increments for the borough 
	b_increments = increments(b.cumulative_array)

	# Daily information
	daily_total = (b.cumulative_array)[-1]
	daily_increment = b_increments[-1]
	daily_percentage = "{:.1f}".format(100*daily_increment/(daily_total-daily_increment))

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

	# Collect data on the selected boroughs
	select_boroughs = lambda tup : tup[1]
	selected_boroughs = filter(select_boroughs,checkbox_items)

	cases_rel_list = []
	area_list = []
	for borough_name,_ in selected_boroughs:
		b = Borough.objects.get(name__exact=borough_name)
		cases_rel_list.append(relative_cases_array(b.cumulative_array, b.population))
		area_list.append(borough_name)

	# Collect data on London
	l = Borough.objects.get(name__exact='London')
	cases_rel_lon = relative_cases_array(l.cumulative_array, l.population)

	# Collect date array
	d = Dates.objects.get()

	# Get the date of the latest update
	last_update = (d.dates_array)[-1]

	cumul_rel = cumulative_plot_rel(d.dates_array,cases_rel_list,area_list,cases_rel_lon)

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
