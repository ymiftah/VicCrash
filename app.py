# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd

from utils import df, top_roads

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
    ]),

    dcc.Graph(
        id='yearlytrends',
    ),

    html.H2(children='Hourly ditribution of accidents'),

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
    ),

    html.H2(children='Leading type of severe accidents'),

    dcc.Graph(
        id='accident-type',
    ),

    html.Label('Year'),
    dcc.RangeSlider(
        df['ACCIDENTYEAR'].min(),
        df['ACCIDENTYEAR'].max(),
        step=None,
        id='year-slider-3',
        value=[df['ACCIDENTYEAR'].min(), df['ACCIDENTYEAR'].max()],
        marks={str(year): str(year) for year in df['ACCIDENTYEAR'].unique()},
    )
])

@app.callback(
    Output('yearlytrends', 'figure'),
    Input('colors', 'value'))
def update_graph_year(colors):
    fig = px.histogram(df.sort_values(colors), x="ACCIDENTYEAR", y="crashes",
             color=colors, barmode='stack')
    fig.update_xaxes(title='Year')
    fig.update_yaxes(title='Number of crashes')
    fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')
    return fig

order = df[['Accident Type Desc', 'crashes']].groupby('Accident Type Desc').sum().sort_values('crashes', ascending=False).index
order_dca = df[['DCA Description', 'crashes']].groupby('DCA Description').sum().sort_values('crashes', ascending=False).index
        
@app.callback(
    Output('hourly_accidents', 'figure'),
    Input('hour-colors', 'value'))
def update_graph_hour(colors):
    fig = px.histogram(df.sort_values(colors),
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
    x=[-37.714498206039806, 144.97739777117712]
    filter = (df.SEVERITY==1) & (df.ACCIDENTYEAR <= value[1]) & (df.ACCIDENTYEAR >= value[0])
    fig = px.scatter_mapbox(df[filter], lat='Lat', lon='Long', zoom=8,
        mapbox_style="open-street-map",
        hover_data=['ACCIDENT_NO', 'NO_PERSONS_KILLED', 'Accident Type Desc', 'DCA Description',
        'Day Week Description', 'Light Condition Desc', 
       'Surface Cond Desc', 'ROAD_NAME','SPEED_ZONE'])
    return fig

@app.callback(
    Output('roads', 'figure'),
    Input('roads-colors', 'value'),
    Input('roads-slider', 'value'),
    Input('year-slider-2', 'value'))
def update_roads(color, slider, value):
    filter = (df.SEVERITY<=slider) & (df.ACCIDENTYEAR <= value[1]) & (df.ACCIDENTYEAR >= value[0])

    frame = df[filter]
    top_roads = frame.groupby('ROAD_NAME').size().sort_values(ascending=False).head(30).index
    frame=frame[(frame.ROAD_NAME.isin(top_roads))].sort_values(color)
    fig = px.histogram(frame, x="ROAD_NAME", y="crashes",
             color=color, barmode='stack',
             category_orders={'ROAD_NAME':top_roads , 'DCA Description':order_dca})
    fig.update_yaxes(title='Fatal accidents')
    return fig

@app.callback(
    Output('accident-type', 'figure'),
    Input('year-slider-3', 'value'))
def update_accident_type(years):
    severe = df[(df.SEVERITY <= 2) & \
            (severe.ACCIDENTYEAR >= years[0]) & (severe.ACCIDENTYEAR <= years[1])]
    aa = severe[['ACCIDENTYEAR', 'DCA Description', 'crashes']].groupby(['ACCIDENTYEAR', 'DCA Description']).sum().reset_index()
    top10 = aa.groupby('DCA Description')['crashes'].sum().sort_values().index[-10:]
    aa = aa[aa['DCA Description'].isin(top10)]
    fig = px.line(aa, x="ACCIDENTYEAR", y="crashes", color='DCA Description',
        title='Leading Type of Severe Accidents',
        category_orders={'DCA Description':order_dca})
    fig.update_yaxes(title='Severe Accidents')
    return fig

if __name__ == '__main__':
    app.run_server(debug=False)