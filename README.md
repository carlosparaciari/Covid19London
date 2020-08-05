# Covid-19 app for London boroughs and Italian provinces

[![Build Status](https://travis-ci.com/carlosparaciari/Covid19London.svg?branch=master)](https://travis-ci.com/carlosparaciari/Covid19London)

This app provides up-to-date graphs showing the cumulative cases in the different boroughs of London, as well as Italian provinces. The absolute number of cases is shown for each borough (province) individually, and the infection's numbers (relative to 100,000 people) in different boroughs (provinces) can be compared. Additionally, the trend of cases and weekly increments can be compared between all boroughs (provinces). The app can be found at this [link](https://covid-19-london.herokuapp.com/plots/). Due to restrictions imposed by the server hosting the project ([Heroku](https://www.heroku.com/)), the app might need several seconds before responding when first approached. 

The app is built using the [Django framework](https://www.djangoproject.com/), it uses [PostgreSQL](https://www.postgresql.org/) for storing the data, and [Celery](http://www.celeryproject.org/) for updating the database every day.

Data on the Covid-19 cases in the UK are obtained from the following [governmental website](https://coronavirus.data.gov.uk/), which provides lots of information on the whole UK coronavirus situation. Data on the Covid-19 cases in Italy are obtained from the following [website](http://opendatadpc.maps.arcgis.com/apps/opsdashboard/index.html#/b0c68bce2cce478eaac82fe38d4138b1), administrated by the Protezione Civile Italiana. We would like to thanks the people working on both website for their great work.

For comments or suggestions on how to improve the app, feel free to raise an issue on this repository.
