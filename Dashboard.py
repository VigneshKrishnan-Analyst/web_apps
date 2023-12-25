import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import callback_context

url = 'https://raw.githubusercontent.com/VigneshKrishnan-Analyst/Recent-Projects/main/Tally%20to%20Zoho%20conversion/Dash/Data/data.csv'
df = pd.read_csv(url)
chart1_df = df.loc[df['Type'] == "Sales"]
chart2_dict_temp = {}
temp_list = ['profit']
for i in df['Account'].loc[df['Type'] != 'Sales'].unique():
    temp_list.append(i)
for exp in temp_list:
    if exp != 'profit':
        chart2_dict_temp[exp] = df['Amount'].loc[df['Account'] == exp].sum()
    else:
        chart2_dict_temp[exp] = (
                    df['Amount'].loc[df['Type'] == 'Sales'].sum() - df['Amount'].loc[df['Type'] != 'Sales'].sum())
chart2_dict = {
    'Expense': chart2_dict_temp.keys(),
    'Amount': chart2_dict_temp.values()
}

chart2_df = pd.DataFrame.from_dict(chart2_dict)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SLATE],
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}]
                )
server = app.server

app.layout = dbc.Container([
    dbc.Row(
        dbc.Col(
            html.H1("Company Private Limited", className='text-xl-center text-capitalize mb-5 mt-5'),
            width=12
        )
    ),
    dbc.Row(
            dbc.Col(
                html.H1("Hover over the pie charts to see the bar graph update !!"),
                width=12
            )
        ),
    dbc.Row(
        [dbc.Col(
            dcc.Graph(id="Sales_mix",
                      figure=px.pie(data_frame=chart1_df, names='Account', values="Amount",
                                    custom_data=['Account'], title='Sales mix as on date'),
                      clickData=None,
                      hoverData=None,
                      config={
                          'staticPlot': False,  # True,False
                          'scrollZoom': True,  # True,False
                          'doubleClick': 'reset',  # 'reset','autosize','reset+autosize',False
                          'showTips': False,  # True,False
                          'displayModeBar': True,  # True,False,'hover'
                          'watermark': True,
                          # modebarButtonsToRemove:['pan2d','select2d']
                      },
                      # className=

                      ), width=4),
            dbc.Col(
                dcc.Graph(id="Expense_mix",
                          figure=px.pie(data_frame=chart2_df, names='Expense', values='Amount',
                                        custom_data=['Expense'], title='Expenses as a percentage of sales'),
                          clickData=None,
                          hoverData=None,
                          config={
                              'staticPlot': False,  # True,False
                              'scrollZoom': True,  # True,False
                              'doubleClick': 'reset',  # 'reset','autosize','reset+autosize',False
                              'showTips': False,  # True,False
                              'displayModeBar': True,  # True,False,'hover'
                              'watermark': True,
                              # modebarButtonsToRemove:['pan2d','select2d']
                          },
                          # className=

                          ), width=4),
            dbc.Col(
                dcc.Graph(id="monthly_breakup",
                          figure={},
                          clickData=None,
                          config={
                              'staticPlot': False,  # True,False
                              'scrollZoom': True,  # True,False
                              'doubleClick': 'reset',  # 'reset','autosize','reset+autosize',False
                              'showTips': False,  # True,False
                              'displayModeBar': True,  # True,False,'hover'
                              'watermark': True,
                              # modebarButtonsToRemove:['pan2d','select2d']
                          },
                          # className=

                          ), width=4)
        ]
    )

])


@app.callback(
    Output(component_id='monthly_breakup', component_property='figure'),
    Input(component_id='Expense_mix', component_property='hoverData'),
    Input(component_id='Sales_mix', component_property='hoverData')
)
def update_monthly_graph_expense(hov_data1, hov_data2):
    graph_id = callback_context.triggered_id
    if graph_id == 'Expense_mix':
        hov_data = hov_data1
        title_x = f'Monthly break-up of expense {hov_data["points"][0]["customdata"][0]}'
        hov = hov_data['points'][0]['customdata'][0]
    elif graph_id == 'Sales_mix':
        hov_data = hov_data2
        title_x = f'Monthly break-up of sales {hov_data["points"][0]["customdata"][0][0]}'
        hov = hov_data['points'][0]['customdata'][0][0]
    else:
        raise dash.exceptions.PreventUpdate

    if hov_data is None or hov_data['points'][0]['customdata'][0] == 'profit':
        dff = df.loc[df['Type'] == 'Sales']
        figure = px.bar(dff, x='Month', y='Amount', title='Monthly Sales data')
    else:
        chart3_df = df.loc[df['Account'] == hov]
        figure = px.bar(chart3_df, x='Month', y='Amount', title=title_x)
    return figure


if __name__ == '__main__':
    app.run_server(debug=True)
