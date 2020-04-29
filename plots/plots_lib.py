# Library for plot tasks and views

import matplotlib.pyplot as plt
import numpy as np

from math import ceil

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
def simple_moving_average(array,period=7.):
    
    if period%2 == 0:
        raise ValueError("period variable should be odd")

    half_period= int((period-1.)/2.)
    size = array.size

    sma = []
    for n in range(size):
        if n < half_period:
            sma.append( np.sum(array[:n+half_period+1])/float(n+half_period+1) )
        elif n > size - (half_period+1):
            sma.append( np.sum(array[n-half_period:])/float(size+half_period-n) )
        else:
            sma.append( np.sum(array[n-half_period:n+half_period+1])/period )

    return np.array(sma)

# Plot of cumulative cases plus increments
def cumulative_plot_abs(dates_str,cases,increment,area):
    
    fig, ax1 = plt.subplots()
    
    ax1.plot(dates_str,cases,linewidth=2) # Cumulative cases in time
    ax1.set_xlabel('Days')
    ax1.set_ylabel('Cases')
    ax1.set_ylim(bottom=0)

    ax2 = ax1.twinx()

    increment_sma = simple_moving_average(increment)
    
    ax2.bar(dates_str,increment,width=1.,color='g',alpha=.5) # Increment in bars
    ax2.plot(dates_str,increment_sma,linewidth=1,color='r')
    ax2.set_ylabel('Daily increments')
    ax2.set_xticks(tick_dates(dates_str))
    
    max_increment = max(increment)
    ax2.set_ylim(top=3*max_increment)
    
    fig.tight_layout()
    plt.close()

    return fig

# Plot of relative cases for different boroughs
def cumulative_plot_rel(dates_str,cases_rel_list,area_list,pop_rel=1e5):

    fig = plt.figure()

    # Divide in boroughs data and London data (London is always passed as last element in list)
    borough_list = cases_rel_list[:-1]
    name_list = area_list[:-1]
    london_data = cases_rel_list[-1]
    
    # Plot all the different boroughs passed to the function
    for cases_rel,area in zip(borough_list,name_list):
        plt.semilogy(dates_str,cases_rel,label=area,linewidth=2)
        
    # Plot London average for comparison
    plt.semilogy(dates_str,london_data,'-.',color='gray',label='London')
    
    # Plot reference increase
    data_size = len(dates_str)
    line_parameters = [(0.3,'r','30%'),(0.2,'y','20%'),(0.1,'g','10%')]
    
    for perc,col,str_perc in line_parameters:
        plt.semilogy(dates_str,line_rel_growth(perc,data_size),'--',color=col,linewidth=0.75,label=str_perc+' daily increase')
    
    plt.title('Density cumulative cases in London boroughs')
    plt.xlabel('Days since 1st relative case')
    plt.ylabel('Cases per '+str(int(pop_rel))+' people (log scale)')
    
    # Maximum value for the y-axis
    max_cases = max([np.max(cases_rel[np.isfinite(cases_rel)]) for cases_rel in cases_rel_list])
    
    plt.xticks(tick_dates(dates_str))
    plt.yticks(*tick_rel(max_cases))
    
    plt.ylim(top=1.2*max_cases,bottom=1)
    
    plt.legend(loc='lower right')
    
    plt.close()
    
    return fig

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
