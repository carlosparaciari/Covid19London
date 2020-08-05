from __future__ import absolute_import, unicode_literals

import pandas as pd
import numpy as np
import requests
import io

from celery import shared_task
from .models import Borough, Province, LondonDate, ItalyDate
from .plots_settings import COVID_DATA_API, POPULATIONS_DIC, COVID_DATA_URL_ITA, COLUMNS_TO_READ_ITA, POPULATIONS_ITA

# This task takes care of the London database

@shared_task
def update_borough_database():

    ## Dates table

    # Load the data for London to get dates array
    london_url = COVID_DATA_API.format(name="London")
    london_data = pd.read_csv(london_url)

    # Find initial and final date for london
    date_array = london_data['SpecimenDate']
    start_date = date_array.min()
    end_date = date_array.max()

    # Create a pad for the dates
    idx = pd.date_range(start_date, end_date)

    # Save the dates into the database
    dates_str = list(idx.strftime("%d-%b-%Y"))

    try:
        d = LondonDate.objects.get()
        d.dates_array = dates_str
    except LondonDate.DoesNotExist:
        d = LondonDate(dates_array=dates_str)

    d.save()

    ## Boroughs' cases and deaths

    # Save the cumulative data into the database
    borough_names = POPULATIONS_DIC.keys()

    for area in borough_names:
        
        borough_url = COVID_DATA_API.format(name=area)
        borough_url = borough_url.replace(' ','%20') # In case there are spaces in the borough name
        borough_data = pd.read_csv(borough_url)

        # Latest number of deaths
        list_deaths = np.array(borough_data['DailyDeaths'])
        deaths_number = int(np.nanmax(list_deaths))
        
        # Drop duplicates, if there are any
        borough_data = borough_data.drop_duplicates()

        # Get the increment of cases (now padded with 0's where no cases were reported)
        borough_data.index = pd.DatetimeIndex(borough_data['SpecimenDate'])
        borough_data_pad = borough_data.reindex(idx,fill_value=0)
        increments = np.array(borough_data_pad['DailyCases'])
        increments = np.nan_to_num(increments) # Replace nan entries with zero

        # Compute the cumulative number of cases out of the increment array
        cases = list(np.cumsum(increments).astype(int))

        try:
            b = Borough.objects.get(name__exact=area)
            b.cumulative_array = cases
            b.latest_deaths = deaths_number
        except Borough.DoesNotExist:
            pop = POPULATIONS_DIC[area]
            b = Borough(name=area,population=pop,cumulative_array=cases,latest_deaths=deaths_number)

        b.save()

# This task takes care of the Italian database

@shared_task
def update_province_database():

    # Load the data into a panda database
    download = requests.get(COVID_DATA_URL_ITA)
    decoded_content = download.content.decode('utf-8')
    full_data = pd.read_csv(io.StringIO(decoded_content))
    data = full_data[COLUMNS_TO_READ_ITA]

    # Make a list of all different province in Italy
    province = data['denominazione_provincia'].drop_duplicates()
    bool_non_prov = ~ province.str.contains('/')
    province = province[bool_non_prov]

    # Make a list of all dates
    dates = data['data'].drop_duplicates()
    dates = pd.to_datetime(dates)
    dates_str = [date.strftime("%d-%b-%Y") for date in dates]

    try:
        d = ItalyDate.objects.get()
        d.dates_array = dates_str
    except ItalyDate.DoesNotExist:
        d = ItalyDate(dates_array=dates_str)

    d.save()

    # Save the cumulative data into the database
    for area in province:

        # Get the data for the relevant borough
        relevant_rows = data['denominazione_provincia'] == area
        provincia_data = data.loc[relevant_rows]

        # If there are duplicate rows, remove them
        provincia_data = provincia_data.drop_duplicates()

        # Compute the cumulative number of cases out of the increment array
        cases = list(provincia_data['totale_casi'])

        try:
            p = Province.objects.get(name__exact=area)
            p.cumulative_array = cases
        except Province.DoesNotExist:
            pop = POPULATIONS_ITA[area]
            p = Province(name=area,population=pop, cumulative_array=cases)

        p.save()
