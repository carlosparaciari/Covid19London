from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse

from .plots_lib import cumulative_cases, relative_cases, regions_trends
from .models import Borough, Province, LondonDate, ItalyDate

def index(request):
	return HttpResponseRedirect(reverse('plots:cumulative_single', args=('London',)))

## LONDON VIEWS

def cumul_abs(request,borough_name):
	context = cumulative_cases(request,LondonDate,Borough,borough_name)

	# London boroughs have information on the total deaths to date
	b = Borough.objects.get(name__exact=borough_name)
	
	context['tot_deaths']=b.latest_deaths
	context['tot_cases']=b.get_single_entry(-1)
	context['mortality']="{:.1f}".format(100*context['tot_deaths']/context['tot_cases'])

	return render(request, 'plots/cumulative_abs.html', context)

def cumul_rel(request):
	context = relative_cases(request,LondonDate,Borough)
	return render(request, 'plots/cumulative_rel.html', context)

def trends(request,borough_name):
	context = regions_trends(request,LondonDate,Borough,borough_name)
	return render(request, 'plots/trends.html', context)

## ITALY VIEWS

def cumul_ita(request,province_name):
	context = cumulative_cases(request,ItalyDate,Province,province_name)
	return render(request, 'plots/cumulative_italy.html', context)

def trends_ita(request,province_name):
	context = regions_trends(request,ItalyDate,Province,province_name)
	return render(request, 'plots/trends_italy.html', context)
