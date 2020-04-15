# Settings for Covid19London Plots app.

COVID_DATA_URL = 'https://fingertips.phe.org.uk/documents/Historic%20COVID-19%20Dashboard%20Data.xlsx'

LOCAL_AREA_SHEET = 5
REGIONS_SHEET = 4

AREA_NAME_COL = 1
DATA_STARTING_COL = 2

BOROUGH_ROWS = range(100,132)
LONDON_ROW = 9
TIME_ROW = 7

POPULATIONS_DIC = {
    "Barking and Dagenham":211998,
    "Barnet":392140,
    "Bexley":247258,
    "Brent":330795,
    "Bromley":331096,
    "Camden":262226,
    "Croydon":385346,
    "Ealing":341982,
    "Enfield":333869,
    "Greenwich":286186,
    "Hackney and City of London":279665,
    "Hammersmith and Fulham":185426,
    "Haringey":270624,
    "Harrow":250149,
    "Havering":257810,
    "Hillingdon":304824,
    "Hounslow":270782,
    "Islington":239142,
    "Kensington and Chelsea":156197,
    "Kingston upon Thames":175470,
    "Lambeth":325917,
    "Lewisham":303536,
    "Merton":206186,
    "Newham":352005,
    "Redbridge":303858,
    "Richmond upon Thames":196904,
    "Southwark":317256,
    "Sutton":204525,
    "Tower Hamlets":317705,
    "Waltham Forest":276700,
    "Wandsworth":326474,
    "Westminster":255324
}