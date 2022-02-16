import pandas as pd
from zipfile import ZipFile

import requests, io

zip_file_url= 'https://vicroadsopendatastorehouse.vicroads.vic.gov.au/opendata/Road_Safety/ACCIDENT.zip'
r = requests.get(zip_file_url)
files = ZipFile(io.BytesIO(r.content))


select=['ACCIDENT_NO', 'ACCIDENTDATE', 'ACCIDENTTIME', 'Accident Type Desc', 'Day Week Description', 'NO_PERSONS_KILLED',
       'DCA Description', 'Light Condition Desc', 'Road Geometry Desc', 'SEVERITY',
       'SPEED_ZONE']
df = pd.read_csv(files.open("ACCIDENT.csv"), usecols=select)
df['ACCIDENTDATE'] = pd.to_datetime(df['ACCIDENTDATE'], infer_datetime_format=True)
df['ACCIDENTTIME'] = pd.to_datetime(df['ACCIDENTTIME'], infer_datetime_format=True)
df['ACCIDENTYEAR'] = df['ACCIDENTDATE'].dt.year
df['ACCIDENTHOUR'] = df['ACCIDENTTIME'].dt.hour

foo = pd.read_csv(files.open('NODE.csv'), usecols = ['ACCIDENT_NO', 'LGA_NAME', 'Lat', 'Long']).drop_duplicates(subset=['ACCIDENT_NO'])
df = df.merge(foo,
    left_on='ACCIDENT_NO',right_on='ACCIDENT_NO', how='inner')

foo = pd.read_csv(files.open('ROAD_SURFACE_COND.csv'), usecols=['ACCIDENT_NO', 'SURFACE_COND', 'Surface Cond Desc']).drop_duplicates(subset=['ACCIDENT_NO'])
df = df.merge(foo, left_on='ACCIDENT_NO',right_on='ACCIDENT_NO', how='left')

foo = pd.read_csv(files.open('ACCIDENT_LOCATION.csv'), usecols=['ACCIDENT_NO', 'ROAD_NAME'])
df = df.merge(foo, left_on='ACCIDENT_NO',right_on='ACCIDENT_NO', how='left')

foo = pd.read_csv(files.open('VEHICLE.csv'), usecols=['ACCIDENT_NO', 'VEHICLE_YEAR_MANUF'])
foo = foo[foo['VEHICLE_YEAR_MANUF'] < 1900]
foo = foo.groupby('ACCIDENT_NO').min().reset_index()
df = df.merge(foo[['ACCIDENT_NO', 'VEHICLE_YEAR_MANUF']], left_on='ACCIDENT_NO',right_on='ACCIDENT_NO', how='left')

foo = pd.read_csv(files.open('SUBDCA.csv'), usecols=['ACCIDENT_NO', 'Sub Dca Code Desc'])
foo = foo.groupby('ACCIDENT_NO').agg(','.join).reset_index()
df = df.merge(foo[['ACCIDENT_NO', 'Sub Dca Code Desc']], left_on='ACCIDENT_NO',right_on='ACCIDENT_NO', how='left')

del(foo)

df['crashes'] = 1
df = df[df.SPEED_ZONE < 200]

top_roads = df.groupby('ROAD_NAME').size().sort_values(ascending=False).head(30).index