# Library for plot tasks and views

import xlrd
import datetime

def xldate_to_str(date,datemode):
    datetime_obj = xlrd.xldate.xldate_as_datetime(date,datemode)
    date_str = datetime_obj.strftime("%d-%b")
    return date_str