import pandas as pd
# import numpy as np
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px
# import plotly.graph_objects as go
import dash_bootstrap_components as dbc
# from dash import callback_context
import os

# Wrangling ----------------------------------------------------------------------------------
url = "https://raw.githubusercontent.com/VigneshKrishnan-Analyst/Recent-Projects/main/Financial%20Dashboard/Data/data.csv"
df = pd.read_csv(url)

cls_df = pd.pivot_table(df, index=['Direction', 'State/UT', 'Year', 'Contact'], columns='Type', values="Amount",
                        aggfunc='sum').reset_index()
cls_df['profit'] = cls_df['Sales']-cls_df['Purchases']-cls_df['Expense']

pl = []
Abs_Amount = []
for i in cls_df['profit']:
    if i > 0:
        pl.append('Profit')
        Abs_Amount.append(abs(i))
    else:
        pl.append('Loss')
        Abs_Amount.append(abs(i))
cls_df['profit/Loss'] = pl
cls_df['Abs_profit'] = Abs_Amount


# App -----------------------------------------------------------------------------------------

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX],
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}]
                )
server = app.server

app.layout = dbc.Container([

    dbc.Row(
        dbc.Col(html.H1("Financial Dashboard",
                        className='text-center text-primary mb-4'),
                width=12)
    ),

dbc.Row([
        dbc.Col(html.Span([html.P( "App provides a visual representation of current status of a company."),
                           html.Br(),
                           html.P("The first Treemap, Highlights the provides a birds eye view of the organization based on Financial year, location and segment."),
                           html.P("Segments performance as green if it is profitable and red if its loss making. Further drill down data can be presented based on availability of data."),
                           html.Br(),
                           html.P('Based on the segment "Clicked or Hovered over", the Pie chart below is updated.'),
                           html.P("The Pie chart is in form of starburst allowing us to visualize the Different components of sales and expenses incurred during the year."),
                           html.Br(),
                           html.P('Based on the expenses "Clicked" the bar graph is updated and further understand the month wise details to have better understanding of the data.')
                        ],
                          className='text-md-left  mb-4'), width=12)
    ]),

    dbc.Row([
        dbc.Col([
            dcc.Graph(id='treemap', figure=px.treemap(
                data_frame=cls_df,
                path=['Year', 'Direction', 'State/UT', ],
                values='Abs_profit',
                color='profit/Loss',
                template='plotly_dark',
                color_discrete_map={
                    'Profit': 'Green',
                    'Loss': 'crimson'},
                custom_data=['State/UT']),
                      )], xs=12, sm=12, md=12, lg=12, xl=12),

        dbc.Row([
            dbc.Col([
                dcc.Graph(id='starburst', figure={},
                          )], xs=12, sm=12, md=12, lg=6, xl=6, className='w-50 p-3'),
            dbc.Col([
                dcc.Graph(id='line', figure={}
                          )], xs=12, sm=12, md=12, lg=6, xl=6, className='w-50 p-3'),
        ]),
    ]),
    dbc.Row(children = [
        dbc.Col([
            html.P("Note:"),
            html.Br(),
            html.P("This Dashboard is created using dummy data as part of presentation."),
            html.Br(),
            html.P("For further queries or oppertunites to collaborate, Please Reach me at:"),
            html.A('vigneshkrishnan097@gmail.com', href = '#',target='_blank'),
            html.Br(),
            html.A('Linkedin', href = 'https://www.linkedin.com/in/vignesh-krishnan-a2136b1bb/',target='_blank'),
            ],
            className = 'text-md-left  mb-4'),
        ]),
])


@app.callback(
    Output(component_id='starburst', component_property='figure'),
    Input(component_id='treemap', component_property='hoverData'),
    Input(component_id='treemap', component_property='clickData'),
    prevent_initial_call=True,
    allow_duplicate=True
)
def update_starburst(hover_data, click_data):
    if click_data is None and hover_data is None:
        entry = "2020"
    elif click_data is None:
        entry = hover_data['points'][0]['id']
    else:
        entry = click_data['points'][0]['id']

    entry_list = entry.split('/')

    for i in entry_list:
        if i in list(df['State/UT']):
            ddf = df.loc[df['State/UT'] == i]
            tx = f'Summarised chart for the {i} State/UT'
        elif i in ["North", "South", "East", "West"]:
            ddf = df.loc[df['Direction'] == i]
            tx = f'Summarised chart for the {i} Region'
        else:
            ddf = df
            tx = 'Summarised chart for the period 2020'

    figure = px.sunburst(ddf, path=['Type', 'Account'], values='Amount', template='plotly_dark',
                         title=tx, custom_data=['State/UT', 'Account'])
    return figure


@app.callback(
    Output(component_id='line', component_property='figure'),
    Input(component_id='starburst', component_property='hoverData'),
    Input(component_id='starburst', component_property='clickData'),
    prevent_initial_call=True,
    allow_duplicate=True
)
def line(hover_data, click_data):
    if click_data is None and hover_data is None:
        entry = ["2020"]
    elif click_data is None:
        entry = hover_data['points'][0]['customdata']
    else:
        entry = click_data['points'][0]['customdata']

    for i in entry:
        if i in list(df['Account']):
            ddf = df.loc[(df['State/UT'] == i) | (df['Account'] == i)]  # Updated condition
            tx = f'Monthly breakup chart for the Account {i}'  # Updated title
        else:
            ddf = df
            tx = 'Monthly breakup chart for the period 2020'

    figure = px.bar(ddf, x="Month", y='Amount', template='plotly_dark', color="Account",
                    title=tx)
    return figure

if __name__ == '__main__':

    app.run_server(debug=True)
