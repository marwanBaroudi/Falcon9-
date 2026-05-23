# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    dcc.Dropdown(id='site-dropdown',
                 options=[
                     {'label': "All Sites", 'value': "ALL"},
                     {'label': "CCAFS LC-40", 'value': "CCAFS LC-40"},
                     {'label': "VAFB SLC-4E", 'value': "VAFB SLC-4E"},
                     {'label': "KSC LC-39A", 'value': "KSC LC-39A"},
                     {'label': "CCAFS SLC-40", 'value': "CCAFS SLC-40"}],
                 value='ALL',
                 placeholder="Select a Launch Site",
                 searchable=True),
    html.Br(),
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),
    html.P("Payload range (Kg):"),
    dcc.RangeSlider(id='payload-slider', 
                    min=min_payload, max=max_payload, step=1000, 
                    value=[min_payload, max_payload]),
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TASK 2: Pie chart callback
@app.callback(Output('success-pie-chart', 'figure'),
              Input('site-dropdown', 'value'))
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Only count successes per site
        df = spacex_df[spacex_df['class'] == 1]
        fig = px.pie(df, 
                     names='Launch Site', 
                     title='Total Successful Launches by Site')
    else:
        df = spacex_df[spacex_df['Launch Site'] == entered_site]
        count_df = df['class'].value_counts().reset_index()
        count_df.columns = ['class', 'count']
        count_df['class'] = count_df['class'].map({1: 'Success', 0: 'Failure'})
        fig = px.pie(count_df, 
                     values='count', 
                     names='class', 
                     title=f'Total Success vs. Failure for site {entered_site}')
    return fig

# TASK 4: Scatter chart callback
@app.callback(Output('success-payload-scatter-chart', 'figure'),
             [Input('site-dropdown', 'value'), Input('payload-slider', 'value')])
def get_scatter_chart(entered_site, payload_range):
    low, high = payload_range
    mask = (spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)
    filtered_df = spacex_df[mask]
    if entered_site == 'ALL':
        fig = px.scatter(filtered_df, 
                         x='Payload Mass (kg)', y='class', 
                         color='Booster Version Category',
                         title='Correlation between Payload and Success for All Sites')
    else:
        site_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        fig = px.scatter(site_df, 
                         x='Payload Mass (kg)', y='class', 
                         color='Booster Version Category',
                         title=f'Correlation between Payload and Success for {entered_site}',
                         width=1200, height=500)
    return fig

# Run the app
if __name__ == '__main__':
    app.run()