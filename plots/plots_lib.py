# Library for plot tasks and views

import matplotlib.pyplot as plt
import numpy as np

from math import floor

def increments(cases_array):
    increment_array = np.insert(np.diff(cases_array), 0, cases_array[0])
    return increment_array

def relative_cases_array(cases_array, population, relative_population=1e5):
    return np.array([relative_population*daily_cases/population for daily_cases in cases_array]) 

def tick_dates(dates,number_shown=5):
    interval = floor(len(dates)/number_shown)
    ticks = [dates[n*interval] for n in range(number_shown)]
    return ticks

def tick_rel(max_val):
    integers = [1,2,5]
    orders = [10**x for x in range(6)]
    all_ticks = np.kron(integers,orders)
    ticks_val = list(all_ticks[all_ticks < max_val])
    ticks_lab = [str(val) for val in ticks_val]
    return ticks_val,ticks_lab

def line_rel_growth(perc,size):
    a = np.log10(1+perc)
    line = np.array([10**(a*n) for n in range(size)])
    return line

def cumulative_plot_abs(dates_str,cases,increment,area):
    fig = plt.figure()
    plt.plot(dates_str,cases) # cumulative in time
    plt.bar(dates_str,increment,color='g') # increment in bars
    plt.title(area+' borough (cumulative cases)')
    plt.xlabel('Days')
    plt.ylabel('Cases')
    plt.xticks(tick_dates(dates_str))
    plt.close()
    return fig

def cumulative_plot_rel(dates_str,cases_rel_list,area_list,cases_rel_lon,pop_rel=1e5):
    fig = plt.figure()
    
    # Plot all the different boroughs passed to the function
    for cases_rel,area in zip(cases_rel_list,area_list):
        plt.semilogy(dates_str,cases_rel,label=area,linewidth=2)
        
    # Plot London average for comparison
    plt.semilogy(dates_str,cases_rel_lon,'-.',color='gray',label='London')
    
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
