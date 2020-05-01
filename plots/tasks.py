from __future__ import absolute_import, unicode_literals

import pandas as pd
import numpy as np
import requests
import io

from celery import shared_task
from .models import Borough, Dates
from .plots_settings import COVID_DATA_URL, POPULATIONS_DIC, COLUMN_TO_READ

@shared_task
def update_borough_database():

    # Load the data into a panda database
    download = requests.get(COVID_DATA_URL)
    decoded_content = download.content.decode('utf-8')
    full_data = pd.read_csv(io.StringIO(decoded_content))
    data = full_data[COLUMN_TO_READ]

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
    dates_str = list(idx.strftime("%d-%b-%Y"))

    try:
        d = Dates.objects.get()
        d.dates_array = dates_str
    except Dates.DoesNotExist:
        d = Dates(dates_array=dates_str)

    d.save()

    # Save the cumulative data into the database
    for area in borough_names:

        # Get the data for the relevant borough
        relevant_rows = data['Area name'] == area
        borough_data = data.loc[relevant_rows]

        # Get the increment of cases (now padded with 0's where no cases were reported)
        borough_data.index = pd.DatetimeIndex(borough_data['Specimen date'])
        borough_data_pad = borough_data.reindex(idx,fill_value=0)
        increments = np.array(borough_data_pad['Daily lab-confirmed cases'])
        increments = np.nan_to_num(increments) # Replace nan entries with zero

        # Compute the cumulative number of cases out of the increment array
        cases = list(np.cumsum(increments).astype(int))

        try:
            b = Borough.objects.get(name__exact=area)
            b.cumulative_array = cases
        except Borough.DoesNotExist:
            pop = POPULATIONS_DIC[area]
            b = Borough(name=area,population=pop, cumulative_array=cases)

        b.save()
