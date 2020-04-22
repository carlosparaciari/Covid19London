from __future__ import absolute_import, unicode_literals

import pandas as pd
import io
import requests

from celery import shared_task
from .models import Borough, Dates
from .plots_settings import COVID_DATA_URL, POPULATIONS_DIC

@shared_task
def update_borough_database():

    # Load the data into a panda database
    download = requests.get(COVID_DATA_URL)
    decoded_content = download.content.decode('utf-8')
    full_data = pd.read_csv(io.StringIO(decoded_content))

    column_to_read = ['Area name','Specimen date','Cumulative lab-confirmed cases']
    data = full_data[column_to_read]

    # Select the areas we are interested in
    borough_names = POPULATIONS_DIC.keys()

    # From London we can build the dates array
    relevant_rows = data['Area name'] == 'London'
    London_data = data.loc[relevant_rows]

    # Find initial and final date for london
    date_array = London_data['Specimen date']
    start_date = date_array.min()
    end_date = date_array.max()

    # Create a pad for the dates
    idx = pd.date_range(start_date, end_date)

    # Save the dates into the database
    dates_str = list(idx.strftime("%d-%b"))

    try:
        d = Dates.objects.get()
        d.dates_array = dates_str
    except Dates.DoesNotExist:
        d = Dates(dates_array=dates_str)

    d.save()

    # Save the cumulative data into the database
    for area in borough_names:
        relevant_rows = data['Area name'] == area
        borough_data = data.loc[relevant_rows]
        borough_data.index = pd.DatetimeIndex(borough_data['Specimen date'])
        borough_data_pad = borough_data.reindex(idx,method='pad')
        cases = list(borough_data_pad['Cumulative lab-confirmed cases'])

        try:
            b = Borough.objects.get(name__exact=area)
            b.cumulative_array = cases
        except Borough.DoesNotExist:
            pop = POPULATIONS_DIC[area]
            b = Borough(name=area,population=pop, cumulative_array=cases)

        b.save()