# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd

from utils import df, top_roads

app = Dash(__name__)

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options

app.layout = html.Div(children=[
    html.H1(children='Victoria Car Crashes'),

    html.H2(children='Accidents by year'),

    dcc.Markdown(
        '''
        While the overall number of accidents each year has kept level since 2006, we do notice a striking decrease in severe and fatal accidents since 2016.
        It would be interesting to track measures taken then and see if they could explain this decrease.

        We see a drastic decrease of accidents in 2020, but this was an 'outlier year' as the State of Victoria was on lock-down since March 2020, probably leading to a decrease of vehicle traffic.

        '''),

    html.Div([
        html.Div([
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

    dcc.Markdown(
        '''
        Severe and Fatal accidents are more likely to happen on certain roads, particulary on Princes Highway, Nepean Highway.
        We also notice that 'High Street' is recurring in Severe crashes, it however does not correspond to a single street, but to busy roads accross different towns in the State of Victoria. 
        '''),

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
    Input('colors', 'value'))
def update_graph(colors):
    fig = px.histogram(df.sort_values(colors), x="ACCIDENTYEAR", y="crashes",
             color=colors, barmode='stack')
    fig.update_xaxes(title='Year')
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
             category_orders={'ROAD_NAME':top_roads})
    fig.update_yaxes(title='Fatal accidents')
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)