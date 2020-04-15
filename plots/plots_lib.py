# Library for plot tasks and views

import xlrd
import datetime
import matplotlib.pyplot as plt
import numpy as np

from math import floor

def xldate_to_str(date,datemode):
    datetime_obj = xlrd.xldate.xldate_as_datetime(date,datemode)
    date_str = datetime_obj.strftime("%d-%b")
    return date_str

def increments(cases_array):
	increment_array = np.insert(np.diff(cases_array), 0, cases_array[0])
	return list(increment_array)

def relative_cases_array(cases_array, population, relative_population=1e5):
	return [relative_population*daily_cases/population for daily_cases in cases_array]

def tick_dates(dates,number_shown=5):
    interval = floor(len(dates)/number_shown)
    ticks = [dates[n*interval] for n in range(number_shown+1)]
    return ticks

def cumulative_plot_abs(dates_str,cases,increment,area,figure_size=(7.5,5.5)):
    fig = plt.figure(figsize=figure_size)
    plt.plot(dates_str,cases,linewidth=2) # cumulative in time
    plt.bar(dates_str,increment,color='g') # increment in bars
    plt.title(area+' borough (cumulative cases)')
    plt.xlabel('Days')
    plt.ylabel('Cases')
    plt.xticks(tick_dates(dates_str))
    plt.close()
    return fig