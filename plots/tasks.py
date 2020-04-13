from __future__ import absolute_import, unicode_literals

import requests
import xlrd

from celery import shared_task
from .models import Borough, Dates
from .plots_lib import xldate_to_str
from .plots_settings import COVID_DATA_URL, LOCAL_AREA_SHEET, REGIONS_SHEET, BOROUGH_ROWS, LONDON_ROW, AREA_NAME_COL, DATA_STARTING_COL, POPULATIONS_DIC, TIME_ROW

@shared_task
def update_borough_database():

    # Request data from UK goverment
    r = requests.get(COVID_DATA_URL)

    # Open workbook and collect info on local areas 
    workbook = xlrd.open_workbook(file_contents=r.content)
    worksheet = workbook.sheet_by_index(LOCAL_AREA_SHEET)

    # Fill the borough database 
    for row in BOROUGH_ROWS:
        area = worksheet.cell_value(row, colx=AREA_NAME_COL)
        cases = worksheet.row_values(row, start_colx=DATA_STARTING_COL)

        try:
            b = Borough.objects.get(name__exact=area)
            b.cumulative_array = cases
        except Borough.DoesNotExist:
            pop = POPULATIONS_DIC[area]
            b = Borough(name=area,population=pop, cumulative_array=cases)

            b.save()

    # Add London to the database
    london_sheet = workbook.sheet_by_index(REGIONS_SHEET)

    area = london_sheet.cell_value(LONDON_ROW, colx=AREA_NAME_COL)
    cases = london_sheet.row_values(LONDON_ROW, start_colx=DATA_STARTING_COL)

    try:
        b = Borough.objects.get(name__exact=area)
        b.cumulative_array = cases
    except Borough.DoesNotExist:
        pop = sum(POPULATIONS_DIC.values())
        b = Borough(name=area, population=pop, cumulative_array=cases)

    b.save()

    # Fill the date database
    dates = worksheet.row_values(TIME_ROW, start_colx=DATA_STARTING_COL)

    wdatemode = workbook.datemode
    dates_str = [xldate_to_str(date,wdatemode) for date in dates]

    try:
        d = Dates.objects.get()
        d.dates_array = dates_str
    except Dates.DoesNotExist:
        d = Dates(dates_array=dates_str)
    
    d.save()