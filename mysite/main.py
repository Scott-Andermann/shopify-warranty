#from shopify_analysis import get_skus
import shopify_analysis
import pandas as pd
from update_data import update_csv
import webbrowser
#from dash_demo import dash_demo
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
from datetime import date, datetime
#from updater import updater

from dash import Dash, dcc, html, Input, Output, dash_table

# Press the green button in the gutter to run the script.
#if __name__ == '__main__':
    # while True:
    #     print('Collecting new data from Shopify...')
update_csv()
today = datetime.now()
update_date = today.strftime('%m/%d/%Y')
print(update_date)
        # print('Data collection complete')
        # print('Analyzing data...')



df = pd.read_csv(u'/home/scottwessol/mysite/orders_complete.csv', index_col=0)
df.reset_index(drop=True, inplace=True)
# print(df.tail())
#print(df)

sprayer_selection = ['FZVAAG', 'FZVAAJ', 'FZVAAK']
top_sku, data = shopify_analysis.get_skus(20, df)
prev_year, this_year = shopify_analysis.cumulative_line_chart(df)
month_dict = {
    1:'Jan',
    2:'Feb',
    3:'Mar',
    4:'Apr',
    5:'May',
    6:'Jun',
    7:'Jul',
    8:'Aug',
    9:'Sep',
    10:'Oct',
    11:'Nov',
    12:'Dec'
}
x_axis = []
for i in prev_year.index:
    x_axis.append(month_dict[i.month])
x2_axis = x_axis[:len(this_year)]

app = Dash()

# Styling for various HTML elements
h1_style = {'padding': '10px',
            'text-align': 'center'}
h2_style = {'background-color': '#aed99e',
            'padding': '10px'}
div_style = {'border': '2px solid gray',
            'font-family': 'sans-serif'}
#p_style = {'font-family': 'sans-serif'}

selection = ['Top 5', 'Top 10', 'Top 20']

app.layout = html.Div(children=[
    html.Div([
        html.P(children = ['Last updated: ', str(today)])
            ], style=div_style),
    html.Div([
        html.H1('WESSOL Warranty Dashboard', style=h1_style)]),
            html.Div([
    html.H2('All Claims - Rolling 12 Months', style=h2_style),
    dcc.Graph(id='graph_all',
              figure={
                  'data': [
                      {'x': x_axis, 'y': prev_year.values, 'type': 'bar', 'name':'Previous Year'},
                      {'x': x2_axis, 'y': this_year.values, 'type': 'bar', 'name':'Current Year'},
                  ]
              })
    ], style=div_style),
    html.Div([
        html.H2('WESSOL Warranty Claims', style=h2_style),
        dcc.Graph(id='graph_1'),
        dcc.Checklist(id='checklist',
                      options=top_sku,
                      value=top_sku[:10],
                      inline=True),
        ], style=div_style),
    html.Div([
        html.H2('YoY Comparison', style=h2_style),
        dcc.Graph(id='graph_comp'),
        dcc.RadioItems(id='radio_1',
                  options=top_sku,
                  value=top_sku[0],
                  inline=True)
    ], style=div_style),
    html.Div([
        html.H2('Sprayers Warranteed', style=h2_style),
        dcc.Graph(id='graph_3'),
        dcc.Checklist(id='checklist_2',
                      options=sprayer_selection,
                      value=sprayer_selection,
                      inline=True),
    ], style=div_style),
    html.Div([
        html.H2('Total Claims', style=h2_style),
        dcc.Graph(id='graph_2'),
        dcc.RadioItems(id='radio',
                      options=['Top 5', 'Top 10', 'Top 20'],
                      value='Top 10',
                      inline=True)
    ], style=div_style),
    html.Div([
        html.H2('Data', style=h2_style),
        html.H4('Sorted by top 20 claimed part numbers in the previous month'),
        html.P('All time highest claimed part numbers shown along with top 20 from the previous month'),
        dash_table.DataTable(data=data.to_dict('records'),
                             sort_action='native')
    ],style=div_style)

])

@app.callback(
    Output('graph_1', 'figure'),
    Input('checklist', 'value'))
def update_line_chart(top_sku):
    df1 = shopify_analysis.parse_line_chart(20, df)
    mask = df1.SKU.isin(top_sku)
    fig = px.line(df1[mask], x='Date', y='Quantity', color='SKU', markers=True)
    return fig

@app.callback(
    Output('graph_3', 'figure'),
    Input('checklist_2', 'value'))
def update_sprayer_chart(sprayer_selection):
    df2 = shopify_analysis.parse_sprayers_only(sprayer_selection, df)
    mask = df2.SKU.isin(sprayer_selection)
    fig = px.line(df2[mask], x='Date', y='Quantity', color='SKU', markers=True)
    return fig

@app.callback(
    Output('graph_2', 'figure'),
    Input('radio', 'value'))
def update_bar_chart(selection):
    if selection == 'Top 10':
        num = 10
    elif selection == 'Top 5':
        num = 5
    else: num = 20
    df3, line_df = shopify_analysis.parse_bar_chart(num, df)

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=df3.index, y=df3.values))
    fig.add_trace(go.Scatter(x=line_df.index, y=line_df.values), secondary_y=True)

    return fig

@app.callback(
    Output('graph_comp', 'figure'),
    Input('radio_1', 'value'))
def update_comparison_chart(sku):
    # parse by entered sku
    df4 = shopify_analysis.parse_line_chart(20, df)
    today = date.today().year
    #print(today)
    #
    df_prev = df4.loc[df4['Year'] == today-1]
    df_curr = df4.loc[df4['Year'] == today]
    #print(df_prev)
    mask_prev = df_prev.SKU.isin([sku])
    mask = df_curr.SKU.isin([sku])

    #print(df_prev[mask_prev])
    #print(df_curr[mask])

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=df_prev[mask_prev].Month, y=df_prev[mask_prev].Quantity, name=today-1))
    fig.add_trace(go.Scatter(x=df_curr[mask].Month, y=df_curr[mask].Quantity, name=today))
    return fig


#app.run_server(debug=True)
#updater()
print('running')
