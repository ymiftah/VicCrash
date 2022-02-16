import pandas as pd
from zipfile import ZipFile

import requests, io

zip_file_url= 'https://vicroadsopendatastorehouse.vicroads.vic.gov.au/opendata/Road_Safety/ACCIDENT.zip'
r = requests.get(zip_file_url)
files = ZipFile(io.BytesIO(r.content))

df = pd.read_csv(files.open("ACCIDENT.csv"))
df['ACCIDENTDATE'] = pd.to_datetime(df['ACCIDENTDATE'])
df['ACCIDENTTIME'] = pd.to_datetime(df['ACCIDENTTIME'])
df['ACCIDENTYEAR'] = df['ACCIDENTDATE'].dt.year
df['ACCIDENTHOUR'] = df['ACCIDENTTIME'].dt.hour

df_node = pd.read_csv(files.open('NODE.csv')).drop_duplicates(subset=['ACCIDENT_NO'])

df = df.merge(df_node[['ACCIDENT_NO', 'LGA_NAME', 'Lat', 'Long']],
    left_on='ACCIDENT_NO',right_on='ACCIDENT_NO', how='inner')

foo = pd.read_csv(files.open('ROAD_SURFACE_COND.csv')).drop_duplicates(subset=['ACCIDENT_NO'])
df = df.merge(foo[['ACCIDENT_NO', 'SURFACE_COND', 'Surface Cond Desc']], left_on='ACCIDENT_NO',right_on='ACCIDENT_NO', how='left')

foo = pd.read_csv(files.open('ACCIDENT_LOCATION.csv'))
df = df.merge(foo[['ACCIDENT_NO', 'ROAD_NAME', 'ROAD_TYPE', 'ROAD_NAME_INT', 'ROAD_TYPE_INT']], left_on='ACCIDENT_NO',right_on='ACCIDENT_NO', how='left')

foo = pd.read_csv(files.open('VEHICLE.csv'))
foo = foo[['ACCIDENT_NO', 'VEHICLE_YEAR_MANUF']]
foo.drop(foo[foo['VEHICLE_YEAR_MANUF'] < 1900].index, inplace=True)
foo = foo.groupby('ACCIDENT_NO').min().reset_index()
df = df.merge(foo[['ACCIDENT_NO', 'VEHICLE_YEAR_MANUF']], left_on='ACCIDENT_NO',right_on='ACCIDENT_NO', how='left')

foo = pd.read_csv(files.open('SUBDCA.csv'))
foo = foo[['ACCIDENT_NO', 'Sub Dca Code Desc']]
foo = foo.groupby('ACCIDENT_NO').agg(','.join).reset_index()
df = df.merge(foo[['ACCIDENT_NO', 'Sub Dca Code Desc']], left_on='ACCIDENT_NO',right_on='ACCIDENT_NO', how='left')


select = ['ACCIDENT_NO', 'ACCIDENTDATE', 'ACCIDENTTIME',
       'Accident Type Desc', 'Day Week Description',
       'DCA Description',  'Light Condition Desc',
       'NO_OF_VEHICLES', 'NO_PERSONS', 'NO_PERSONS_INJ_2',
       'NO_PERSONS_INJ_3', 'NO_PERSONS_KILLED', 'NO_PERSONS_NOT_INJ',
       'POLICE_ATTEND', 'Road Geometry Desc', 'SEVERITY',
       'SPEED_ZONE', 'ACCIDENTYEAR', 'ACCIDENTHOUR', 'LGA_NAME', 'Lat', 'Long',
       'Surface Cond Desc', 'ROAD_NAME', 'ROAD_TYPE',
       'ROAD_NAME_INT', 'ROAD_TYPE_INT']
df = df[select]
df['crashes'] = 1
df = df[df.SPEED_ZONE < 200]

top_roads = df.groupby('ROAD_NAME').size().sort_values(ascending=False).head(30).index