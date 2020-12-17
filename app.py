import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import numpy as np
import geopandas as gpd
import plotly.graph_objects as go

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

airports = pd.read_csv("airports.csv")
flights = pd.read_csv("flights.csv", low_memory = False)

# fill in missing values
#airports.loc[airports['LATITUDE'].isnull(),]
airports.loc[airports['CITY'] == 'Panama City', 'LATITUDE'] = 8.983333
airports.loc[airports['CITY'] == 'Panama City', 'LONGITUDE'] = -79.516670
airports.loc[airports['CITY'] == 'Plattsburgh', 'LATITUDE'] = 44.6994873
airports.loc[airports['CITY'] == 'Plattsburgh', 'LONGITUDE'] = -73.4529124
airports.loc[airports['CITY'] == 'St. Augustine', 'LATITUDE'] = 29.9012
airports.loc[airports['CITY'] == 'St. Augustine', 'LONGITUDE'] = -81.3124

# get rid of unnessary variables and only include unique combination
updated_flights = flights[['AIRLINE', 'ORIGIN_AIRPORT', 'DESTINATION_AIRPORT']]
updated_flights = updated_flights.drop_duplicates(['AIRLINE', 'ORIGIN_AIRPORT', 'DESTINATION_AIRPORT'])
updated_airports = airports[['IATA_CODE', 'AIRPORT', 'STATE', 'LATITUDE', 'LONGITUDE']]

origin = pd.merge(updated_flights, updated_airports, left_on = "ORIGIN_AIRPORT", right_on = "IATA_CODE")
origin = origin.sort_values(by = ['AIRLINE', 'ORIGIN_AIRPORT', 'DESTINATION_AIRPORT'])
# modify columns' names
origin = origin.rename(columns = {'LATITUDE':'LATITUDE_STAR', 'LONGITUDE':'LONGITUDE_STAR'})


destination = pd.merge(updated_flights, updated_airports, left_on = "DESTINATION_AIRPORT", right_on = "IATA_CODE")
destination = destination.sort_values(by = ['AIRLINE', 'ORIGIN_AIRPORT', 'DESTINATION_AIRPORT'])
# modify columns' names
destination = destination.rename(columns = {'LATITUDE':'LATITUDE_END', 'LONGITUDE':'LONGITUDE_END'})


# create id columns for both origin and destination sets
origin['ID'] = range(0, len(origin))
destination['ID'] = range(0, len(destination))

# merge origin and destination
flights_path = pd.merge(origin, destination, on = "ID")
flights_path = flights_path.rename(columns = {'AIRLINE_x':'AIRLINE', 'ORIGIN_AIRPORT_x':'ORIGIN_AIRPORT', 
                                                'DESTINATION_AIRPORT_x':'DESTINATION_AIRPORT', 'STATE_x':'STATE', 
                                                'AIRPORT_x':'AIRPORT'})
# subset necessary variable only
flights_path = flights_path[['AIRLINE', 'ORIGIN_AIRPORT', 'DESTINATION_AIRPORT', 'AIRPORT', 'LATITUDE_STAR', 
             'LONGITUDE_STAR', 'LATITUDE_END', 'LONGITUDE_END', 'STATE']]



app.layout = html.Div([
    dcc.Dropdown(id = 'airport', 
                options = [{'label': i, 'value': i} for i in flights_path['AIRPORT'].unique()], 
                value = "Ted Stevens Anchorage International Airport"), 
    dcc.Graph(id='graph')
])


@app.callback(
    Output('graph', 'figure'),
    Input('airport', 'value'))
def update_figure(selected_airport):
    filtered_flights_path = flights_path[flights_path['AIRPORT'] == selected_airport]
    filtered_flights_path = filtered_flights_path.reset_index()

    fig = go.Figure()

    fig.add_trace(go.Scattergeo(
        locationmode = 'USA-states',
        lon = airports['LONGITUDE'],
        lat = airports['LATITUDE'],
        hoverinfo = 'text',
        text = airports['AIRPORT'],
        mode = 'markers',
        marker = dict(
            size = 2,
            color = 'rgb(255, 0, 0)',
            line = dict(
                width = 3,
                color = 'rgba(68, 68, 68, 0)'
            )
        )))

    for i in range(len(filtered_flights_path)):
        fig.add_trace(
            go.Scattergeo(
                locationmode = 'USA-states',
                lon = [filtered_flights_path['LONGITUDE_STAR'][i], filtered_flights_path['LONGITUDE_END'][i]],
                lat = [filtered_flights_path['LATITUDE_STAR'][i], filtered_flights_path['LATITUDE_END'][i]],
                mode = 'lines',
                line = dict(width = 1,color = 'red'),
            )
        )

    fig.update_layout(
        title_text = 'Flight Paths for the Selected Airports',
        showlegend = False,
        geo = dict(
            scope = 'north america',
            projection_type = 'azimuthal equal area',
            showland = True,
            landcolor = 'rgb(243, 243, 243)',
            countrycolor = 'rgb(204, 204, 204)',
        ),
    )

    fig.update_layout(transition_duration=500)

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)