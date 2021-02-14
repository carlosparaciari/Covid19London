# Library for plot tasks and views

import io
import urllib
import base64
import numpy as np
import matplotlib.pyplot as plt
import matplotlib._color_data as mcd

from django.http import Http404
from django.shortcuts import get_object_or_404

from math import ceil
from datetime import datetime

from .forms import DailyCasesForm

## CONTEXT FUNCTIONS

# This function prepare the context for the absolute plots (for both London and Italy)
def cumulative_cases(request,model_date,model_region,regional_name):

    # Get dates array from database and last date of update
    d = model_date.objects.get()
    dates_array = d.get_dates('%d %b %y')
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
            date_requested = date_object.strftime('%d %b %y')
            if date_requested in dates_array:
                date_val = date_object

    date_val_str = date_val.strftime('%d %b %y')

    # Make the dropdown menu
    full_list = [entry for entry in model_region.objects.values_list('name', flat=True)]

    try:
        full_list.remove('London')
        sort_list = np.sort(full_list)
        menu_items = np.append(sort_list,'London')
    except ValueError:
        menu_items = np.sort(full_list)

    # Get relevant region and dates
    b = get_object_or_404(model_region, name__exact=regional_name)

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

    return context

# This function prepare the context for the relative plots (currently only for London)
def relative_cases(request,model_date,model_region):

    # Prepare list of borough to be plotted
    if request.method == 'POST':
        response_post = request.POST
        response_dict = response_post.dict()

        borough_names = model_region.objects.values_list('name',flat=True)
        borough_names = borough_names.exclude(name='London')
        checkbox_items = [(name, name in response_dict) for name in borough_names]
    else:
        queryset_name_cases = model_region.objects.values_list('name','cumulative_array')
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
        b = model_region.objects.get(name__exact=borough_name)
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
    d = model_date.objects.get()
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

    return context

# This function prepare the context for the trend plots (for both London and Italy)
def regions_trends(request,model_date,model_region,regional_name,pop_rel=1e5):

    # Get last date of update
    d = model_date.objects.get()
    last_update = d.get_single_date_str(-1,'%d %B')

    # Make the dropdown menu
    full_list = [entry for entry in model_region.objects.values_list('name', flat=True)]

    try:
        full_list.remove('London')
        sort_list = np.sort(full_list)
        menu_items = np.append(sort_list,'London')
    except ValueError:
        menu_items = np.sort(full_list)

    # Check that regional_name belongs to list
    if not np.isin(regional_name,menu_items):
        raise Http404("Region name does not exists")

    # Collect total number of cases and weekly increases per regional area
    data_points = {}
    pop_list = []

    for area in menu_items:
        b = model_region.objects.get(name__exact=area)

        latest_cases = b.get_single_entry(-1)
        week_old_cases = b.get_single_entry(-7)

        week_increment = latest_cases - week_old_cases

        pop = b.population
        pop_list.append(pop)

        data_points[area] = (pop_rel*latest_cases/pop, pop_rel*week_increment/pop)

    all_data = np.array([[*entry] for entry in data_points.values()]).T
    cases_list, incr_list = all_data

    # Average value of cases and increses over regional areas
    pop_array = np.array(pop_list)

    average_data = np.sum(all_data*pop_array,axis=1)/np.sum(pop_array)
    average_cases, average_incr = average_data

    # Select extreme regions to highligh in the plot
    high_cases = cases_list > average_cases
    high_incr = incr_list > average_incr

    point_list = np.array(list(data_points.items()))
    delta_cases = max(cases_list) - min(cases_list)
    delta_incr = max(incr_list) - min(incr_list)

    # North-East quadrant (high cases and high increase)
    quadrant_NE = np.logical_and(high_cases,high_incr)
    measure_NE = lambda x,y : x/delta_cases + y/delta_incr

    values_NE = extremal_regions(point_list[quadrant_NE],measure_NE)

    # South-East quadrant (high cases and low increase)
    quadrant_SE = np.logical_and(high_cases,~high_incr)
    measure_SE = lambda x,y : x/delta_cases - y/delta_incr

    values_SE = extremal_regions(point_list[quadrant_SE],measure_SE)

    # South-West quadrant (low cases and low increase)
    quadrant_SW = np.logical_and(~high_cases,~high_incr)
    measure_SW = lambda x,y : - x/delta_cases - y/delta_incr

    values_SW = extremal_regions(point_list[quadrant_SW],measure_SW,n=1)

    # North-West quadrant (low cases and high increase)
    quadrant_NW = np.logical_and(~high_cases,high_incr)
    measure_NW = lambda x,y : - x/delta_cases + y/delta_incr

    values_NW = extremal_regions(point_list[quadrant_NW],measure_NW)

    # Plot the regional trends in a scatter plot
    highlights = (values_NE,values_SE,values_SW,values_NW)
    regional_data = data_points[regional_name]

    plot_trend = plot_trends(regional_data,all_data,average_data,highlights)

    # Save plot into buffer and convert to be able to visualise it
    buf = io.BytesIO()
    plot_trend.savefig(buf,format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)

    # Data to pass to the html page
    context = {}
    context['data']=uri
    context['items']=menu_items
    context['current']=regional_name
    context['date']=last_update
    context['rel_num']='{:,}'.format(int(pop_rel))
    context['tot_cases']="{:.1f}".format(regional_data[0])
    context['weekly_inc']="{:.1f}".format(regional_data[1])

    return context

## AUXILIARY FUNCTIONS

# Provide the daily increments from the array of cumulative cases
def increments(cases_array):
    increment_array = np.insert(np.diff(cases_array), 0, cases_array[0])
    return increment_array

# Provide the array of cumulative cases, relative to the population of the borough
def relative_cases_array(cases_array, population, relative_population=1e5):
    return np.array([relative_population*daily_cases/population for daily_cases in cases_array]) 

# Provide the position of the ticks to be shown on the x-axis
def tick_dates(dates,number_shown=8):
    size = len(dates)
    interval = ceil(size/number_shown)
    ticks = np.array([n*interval for n in range(number_shown)])
    return ticks

# Provide the position of the ticks to be shown on the y-axis of the relative plot
def tick_rel(max_val):
    integers = [1,2,5]
    orders = [10**x for x in range(6)]
    all_ticks = np.kron(integers,orders)
    ticks_val = list(all_ticks[all_ticks < max_val])
    ticks_lab = [str(val) for val in ticks_val]
    return ticks_val,ticks_lab

# Provide the line of percental growth for the relative plot
def line_rel_growth(perc,size):
    a = np.log10(1+perc)
    line = np.array([10**(a*n) for n in range(size)])
    return line

# Simple moving average for data array
def simple_moving_average(array,period=7.,stopping=5):
    
    if period%2 == 0:
        raise ValueError("period variable should be odd")

    half_period= int((period-1.)/2.)
    size = array.size

    sma = []
    for n in range(size):

        initial = max(0,n-half_period)
        final = min(size,n+half_period+1)

        sma.append( np.mean(array[initial:final]) )

    sma = np.array(sma)
    sma[-5:] = np.full(5,None)

    return np.array(sma)

# Identify the n region with higher value of the given order measure
def extremal_regions(point_list,order_measure,n=2):
    
    # In case the passed object is not a list
    point_list = list(point_list)
    
    # Order the points with the order measure, and take the first n of them
    point_list.sort(reverse=True,key = lambda tup : order_measure(*tup[1]))
    extremal_points = point_list[:n]
    
    # Record the name of the regions, the number of cases and the weekly increase
    areas_list = np.array([area for area,_ in extremal_points])
    cases_list, incr_list = np.array([[*point] for _,point in extremal_points]).T
    
    return areas_list, cases_list, incr_list

# Prepare the list of the most affected borough in london
#
# INPUT:
#       - queryset : QuerySet object with name of borough and array of cases
#       - treshold : number of borough to check (compare)
#
# OUTPUT:
#       - checkbox_items : list of tuples, with name of borough and boolean for check (compare)
#
def prepare_checklist_boroughs(queryset,treshold=3):
    affected_boroughs = [(name,cases[-1]) for name,cases in queryset]
    affected_boroughs = sorted(affected_boroughs, key=lambda tup: tup[1],reverse = True)
    most_affected_boroughs = [affected_boroughs[iterator][0] for iterator in range(1,treshold+1)]

    checkbox_items = [(name, name in most_affected_boroughs) for name,_ in queryset]

    return checkbox_items

## PLOT FUNCTIONS

# Plot of cumulative cases plus increments
def cumulative_plot_abs(dates_str,cases,increment,area):
    
    plt.rc('xtick',labelsize=12)
    plt.rc('ytick',labelsize=12)

    fig, ax1 = plt.subplots()

    ax1.set_zorder(2)
    ax1.patch.set_visible(False)
    
    ax1.plot(dates_str,cases,linewidth=2) # Cumulative cases in time
    ax1.set_xlabel('Days',size=14)
    ax1.set_ylabel('Cases',size=14)
    ax1.set_ylim(bottom=0)

    ax2 = ax1.twinx()
    ax2.set_zorder(1)

    increment_sma = simple_moving_average(increment)
    
    pltbar = ax2.bar(dates_str,increment,width=1.,color='darkseagreen') # Increment in bar
    ax2.plot(dates_str,increment_sma,linewidth=1,color='r')
    ax2.set_ylabel('Daily increments',size=14)
    ax2.set_xticks(tick_dates(dates_str,number_shown=7))
    
    max_increment = max(increment)
    ax2.set_ylim(top=3*max_increment)

    # Highlight last 5 bars (they are provisional values)
    for n in range(5):
        pltbar[-(n+1)].set_color('forestgreen')

    fig.tight_layout()
    plt.close()

    return fig

# Plot of relative cases for different boroughs
def cumulative_plot_rel(dates_str,cases_rel_list,area_list,col_list,pop_rel=1e5):

    plt.rc('xtick',labelsize=12)
    plt.rc('ytick',labelsize=12)

    fig = plt.figure()

    # Divide in boroughs data and London data (London is always passed as last element in list)
    borough_list = cases_rel_list[:-1]
    name_list = area_list[:-1]
    london_data = cases_rel_list[-1]
    
    # Plot all the different boroughs passed to the function
    for cases_rel,area,col in zip(borough_list,name_list,col_list):
        plt.semilogy(dates_str,cases_rel,label=area,linewidth=2,color=col)
        
    # Plot London average for comparison
    plt.semilogy(dates_str,london_data,'-.',color='gray',label='London')
    
    # Plot reference increase
    data_size = len(dates_str)
    line_parameters = [(0.3,'r','30%'),(0.2,'y','20%'),(0.1,'g','10%')]
    
    for perc,col,str_perc in line_parameters:
        plt.semilogy(dates_str,line_rel_growth(perc,data_size),'--',color=col,linewidth=0.75,label=str_perc+' daily increase')
    
    plt.xlabel('Days since 1st relative case',size=14)
    plt.ylabel('Cases per '+'{:,}'.format(int(pop_rel))+' people (log scale)',size=14)
    
    # Maximum value for the y-axis
    max_cases = max([np.max(cases_rel[np.isfinite(cases_rel)]) for cases_rel in cases_rel_list])
    
    plt.xticks(tick_dates(dates_str))
    plt.yticks(*tick_rel(max_cases))
    
    plt.ylim(top=1.2*max_cases,bottom=1)
    
    plt.legend(loc='lower right')
    
    plt.close()
    
    return fig

# Plot each regional area as a point  on a 2D plot with
# x-axis : the total number of cases reported to date
# y-axis : the increse in the number of cases reported during the week
def plot_trends(region_data,all_data,average_data,highlights):
    
    # Unpacking data
    cases_list, incr_list = all_data
    average_cases, average_incr = average_data

    plt.rc('xtick',labelsize=12)
    plt.rc('ytick',labelsize=12)

    fig = plt.figure()
    
    # Plot all region for reference
    plt.scatter(*all_data, c='lightgray',marker='.')

    # Divide the plot between high and low increments (compared to average)
    xmax = max(cases_list)
    xmin = min(cases_list)
    plt.hlines(average_incr, xmin, xmax, linestyles='--',linewidth=.6)

    # Divide the plot between high and low cases (compared to average)
    ymax = max(incr_list)
    ymin = min(incr_list)
    plt.vlines(average_cases, ymin, ymax, linestyles='--',linewidth=.6)

    # Plot the average point
    plt.scatter([average_cases], [average_incr], c='black',marker='.')

    # Plot the highlighted regions in the different quadrants
    colours = ('red','orange','green','orange')
    
    for val, col in zip(highlights,colours):
        plt.scatter(val[1], val[2], c=col,marker='.')
    
    # Annotate the highlighted points with the corresponding regional name
    delta_y = 0.01*(ymax-ymin)

    for areas, cases, incrs in highlights:
        for text, x, y in zip(areas, cases, incrs):
            plt.annotate(text, (x,y+delta_y),size=14)        
    
    # Highlight the region of interest
    plt.scatter(*region_data,marker="X",zorder=10)
    
    plt.box(on=None)
    
    plt.xlabel('Total number of cases',size=14)
    plt.ylabel('Weekly increase in cases',size=14)
    
    plt.close()
    
    return fig