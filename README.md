# Covid-19 app for London boroughs

[![Build Status](https://travis-ci.com/carlosparaciari/Covid19London.svg?branch=master)](https://travis-ci.com/carlosparaciari/Covid19London)

This app provides up-to-date graphs showing the cumulative cases in the different boroughs of London. The absolute number of cases is shown for each borough individually, and the infection's numbers (relative to 100,000 people) in different boroughs can be compared. The app can be found at this [link](https://covid-19-london.herokuapp.com/plots/). Due to restrictions imposed by the server hosting the project ([Heroku](https://www.heroku.com/)), the app might need several seconds before responding when first approached. 

The app is built using the [Django framework](https://www.djangoproject.com/), it uses [PostgreSQL](https://www.postgresql.org/) for storing the data, and [Celery](http://www.celeryproject.org/) for updating the database every day.

Data on the Covid-19 cases in the UK are obtained directly from the following [governmental website](https://coronavirus.data.gov.uk/), which provides lots of information on the whole UK coronavirus situation. We would like to thanks the people working on this website for their great service to the nation.

For comments or suggestions on how to improve the app, feel free to raise an issue on this repository.