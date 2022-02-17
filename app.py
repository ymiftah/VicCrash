# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd

from utils import *

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

app.layout = html.Div(children=[
    html.H1(children='Victoria Car Crashes'),

    html.H2(children='Accidents by year'),

    html.Div([
        html.Div([
            html.Label('Category selection'),
            dcc.Dropdown(
                ['Light Condition Desc', 'Road Geometry Desc', 'SEVERITY',
                'SPEED_ZONE', 'Surface Cond Desc'],
                'SEVERITY',
                id='colors'
            ),
        ], style={'width': '45%', 'display': 'inline-block'}),

        html.Div([
            html.Label('Severity'),
            dcc.Slider(
                1,
                4,
                step=1,
                id='yearly-slider',
                value=4,
                marks={str(i): str(i) for i in range(1,5)},
            ),
        ], style={'width': '30%', 'float': 'right', 'display': 'inline-block', 'padding': 10, 'flex': 1})
    ], style={'display': 'flex', 'flex-direction': 'row'}
    ),

    dcc.Graph(
        id='yearlytrends',
    ),

    html.H2(children='Leading types of severe accidents'),

    html.Div([
        html.Label('Severity'),
        dcc.Slider(
            1, 2,
            step=1,
            id='types-slider',
            value=2,
            marks={str(i): str(i) for i in range(1,3)},
        ),
        ], style={'width': '30%'}
    ),

    dcc.Graph(
        id='accident-type'
    ),

    html.H2(children='Hourly distribution of accidents'),

    html.Div([
        html.Div([
            html.Label('Category selection'),
            dcc.Dropdown(
                ['Accident Type Desc', 'Road Geometry Desc', 'SEVERITY',
                'SPEED_ZONE', 'Surface Cond Desc'],
                'SEVERITY',
                id='hour-colors'
            ),
        ], style={'width': '45%', 'display': 'inline-block'}),
    ]),

    dcc.Graph(
        id='hourly_accidents',
    ),

    dcc.RangeSlider(
        df['ACCIDENTYEAR'].min(),
        df['ACCIDENTYEAR'].max(),
        step=None,
        id='hourly-year-slider',
        value=[df['ACCIDENTYEAR'].min(), df['ACCIDENTYEAR'].max()],
        marks={str(year): str(year) for year in df['ACCIDENTYEAR'].unique()},
    ),

    html.H2(children='Map of fatal accidents'),

    dcc.Graph(
        id='map',
    ),

    dcc.RangeSlider(
        df['ACCIDENTYEAR'].min(),
        df['ACCIDENTYEAR'].max(),
        step=None,
        id='year--slider',
        value=[df['ACCIDENTYEAR'].min(), df['ACCIDENTYEAR'].max()],
        marks={str(year): str(year) for year in df['ACCIDENTYEAR'].unique()},
    ),

    html.H2(children='Dangerous Roads'),

    html.Div([

        html.Div([
            html.Label('Category selection'),
            dcc.Dropdown(
                ['Light Condition Desc', 'Road Geometry Desc',
                'SPEED_ZONE', 'Surface Cond Desc', 'DCA Description', 'SEVERITY'],
                'SEVERITY',
                id='roads-colors'
            ),
        ], style={'width': '45%', 'display': 'inline-block'}),

        html.Div([
            html.Label('Severity'),
            dcc.Slider(
                1,
                4,
                step=1,
                id='roads-slider',
                value=4,
                marks={str(i): str(i) for i in range(1,5)},
            ),
        ], style={'width': '30%', 'float': 'left', 'display': 'inline-block', 'padding': 10, 'flex': 1})
    ], style={'display': 'flex', 'flex-direction': 'row'}),

    dcc.Graph(
        id='roads',
    ),

    html.Label('Year'),
    dcc.RangeSlider(
        df['ACCIDENTYEAR'].min(),
        df['ACCIDENTYEAR'].max(),
        step=None,
        id='year-slider-2',
        value=[df['ACCIDENTYEAR'].min(), df['ACCIDENTYEAR'].max()],
        marks={str(year): str(year) for year in df['ACCIDENTYEAR'].unique()},
    )
])

@app.callback(
    Output('yearlytrends', 'figure'),
    Input('colors', 'value'),
    Input('yearly-slider', 'value'))
def update_graph_year(colors, slider):
    fig = px.histogram(df[df.SEVERITY <= slider].sort_values(colors),
            x="ACCIDENTYEAR", y="crashes",
            color=colors, barmode='stack')
    fig.update_xaxes(title='Year')
    fig.update_yaxes(title='Number of crashes')
    fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')
    return fig

@app.callback(
    Output('accident-type', 'figure'),
    Input('types-slider', 'value'))
def update_accident_types(slider):
    severe = df[df.SEVERITY <= slider]
    aa = severe[['ACCIDENTYEAR', 'DCA Description', 'crashes']].groupby(['ACCIDENTYEAR', 'DCA Description']).sum().reset_index()
    top10 = aa.groupby('DCA Description')['crashes'].sum().sort_values(ascending=False).index[:10]
    aa = aa[aa['DCA Description'].isin(top10)]
    fig = px.line(aa, x="ACCIDENTYEAR", y="crashes", color='DCA Description',
        category_orders={'DCA Description':top10})
    fig.update_yaxes(title='Severe Accidents')
    return fig

@app.callback(
    Output('hourly_accidents', 'figure'),
    Input('hourly-year-slider', 'value'),
    Input('hour-colors', 'value'))
def update_graph_hour(value, colors):
    filter = (df.ACCIDENTYEAR <= value[1]) & (df.ACCIDENTYEAR >= value[0])
    fig = px.histogram(df[filter].sort_values(colors),
            x="ACCIDENTHOUR", y="crashes",
            color=colors, barmode='stack',
            category_orders={'SEVERITY':list(range(5)), 'Accident Type Desc': order, 'DCA Description':order_dca})
    fig.update_xaxes(title='Hour')
    fig.update_yaxes(title='Number of crashes')
    fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')
    return fig

@app.callback(
    Output('map', 'figure'),
    Input('year--slider', 'value'))
def update_map(value):
    filter = (df.SEVERITY==1) & (df.ACCIDENTYEAR <= value[1]) & (df.ACCIDENTYEAR >= value[0])
    fig = px.scatter_mapbox(df[filter], lat='Lat', lon='Long', zoom=8,
        mapbox_style="open-street-map",
        hover_data=['ACCIDENT_NO', 'NO_PERSONS_KILLED', 'Accident Type Desc', 'DCA Description',
            'Day Week Description', 'Light Condition Desc', 'Surface Cond Desc', 'ROAD_NAME','SPEED_ZONE'])
    return fig

@app.callback(
    Output('roads', 'figure'),
    Input('roads-colors', 'value'),
    Input('roads-slider', 'value'),
    Input('year-slider-2', 'value'))
def update_roads(color, slider, value):
    frame = df[(df.SEVERITY<=slider) & (df.ACCIDENTYEAR <= value[1]) & (df.ACCIDENTYEAR >= value[0])]
    top_roads = frame.groupby('ROAD_NAME').size().sort_values(ascending=False).head(30).index
    order_dca = frame[['DCA Description', 'crashes']].groupby('DCA Description').sum().sort_values('crashes', ascending=False).index


    frame = frame[(frame.ROAD_NAME.isin(top_roads))].sort_values(color)
    fig = px.histogram(frame, x="ROAD_NAME", y="crashes",
             color=color, barmode='stack',
             category_orders={'ROAD_NAME':top_roads , 'DCA Description':order_dca})
    fig.update_yaxes(title='Fatal accidents')
    return fig

if __name__ == '__main__':
    app.run_server(debug=False)