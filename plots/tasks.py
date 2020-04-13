from __future__ import absolute_import, unicode_literals

import requests
import xlrd

from celery import shared_task
from .models import Borough
from .plots_settings import COVID_DATA_URL, LOCAL_AREA_SHEET, BOROUGH_ROWS, AREA_NAME_COL, DATA_STARTING_COL, POPULATIONS_DIC

@shared_task
def update_borough_database():

    # Request data from UK goverment
    r = requests.get(COVID_DATA_URL)

    # Open workbook and collect info on local areas 
    workbook = xlrd.open_workbook(file_contents=r.content)
    worksheet = workbook.sheet_by_index(LOCAL_AREA_SHEET)

    # Fill the database 
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
