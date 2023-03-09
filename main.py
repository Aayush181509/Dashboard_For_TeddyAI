from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go
import plotly.express as px
import dash
from flask import Flask
import dash_bootstrap_components as dbc
import pandas as pd
import ast

# App initialization
server=Flask(__name__)
app = dash.Dash(__name__,server =server,external_stylesheets=[dbc.themes.BOOTSTRAP,dbc.icons.BOOTSTRAP])
colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

# Loading the Data from a file
data=pd.read_json("/home/aayush/Documents/Otermans_Institute/data_analysis_task/data/teddyai-123ab-default-rtdb-export(2).json")[2:][['IDC']].transpose()

# Data Preprocessing and converting into normalized data_frame
def time_process(data_df):
    time_list=[]
    time_dict=dict()
    for i in data_df['IDC']:
        for j in i.values():
            for x,y in j.items():
                if x=='timeSpent':
                    for key,value in y.items():
                        if value=='':
                            value=0
                            time_dict[key]=float(value)
                        else:
                            value=value[:-1]
                            value=value.replace(',','.')
                            time_dict[key]=float(value)
                        time_dict[key]=float(value)
                    time_list.append(time_dict.copy())
    return time_list

def value_normalization(user_data):
    new_list_for=[]
    dict_for_this=dict()
    for i in user_data:
        for k,v in i.items():
            if not isinstance(v,dict):
                dict_for_this[k]=v

            else:
                for key,value in v.items():
                    dict_for_this[k+'_'+key]=value

    #     print(dict_for_this)
        new_list_for.append(dict_for_this.copy())
    return new_list_for

def process_data(data_df):
    user_data=[]
    for i in data_df['IDC']:
        for j in i.values():
            user_data.append(j)
    user_data = pd.DataFrame(user_data)
    user_data.timeSpent=time_process(data_df)
    user_data = list(user_data.T.to_dict().values())
    user_data=value_normalization(user_data)
    user_data = pd.DataFrame(user_data)
    user_data['timeSpent_total'] = user_data.iloc[:,7:14].sum(axis='columns')
    date=user_data['dateTime'].apply(lambda x:x.split(' ',1)[0])
    time=user_data['dateTime'].apply(lambda x:x.split(' ',1)[1])
    user_data.insert(2,'Date', date)
    user_data.insert(3,'Time', time)
    user_data.drop('dateTime',axis='columns',inplace=True)
    return user_data

user_data=process_data(data.T)

timeSpent_total=pd.DataFrame(user_data.iloc[:,7:14].sum())

# Individual Student Personal Records and Time Spent on different section pie chart representation
piePR = dcc.Graph(id="graph")
pieTS = dcc.Graph(id="graph_TS")
@app.callback(
    Output("values","value"),
    Output("values","options"), 
    Input("names", "value")) 
def update_output_div(input_value):
    return list(data[input_value][0].keys())[0],list(data[input_value][0].keys())

@app.callback(
    # Output("graph_TS","figure"),
    Output("graph", "figure"),
    Input("names", "value"), 
    Input("values", "value"))
def generate_chart(names, values):
    d=data[names][0][values]['personalRecords']
    df = pd.DataFrame.from_dict(d, orient='index', columns=['count'])
    colors = ['gold', 'mediumturquoise', 'darkorange', 'lightgreen']
    fig = go.Figure(data=[go.Pie(labels=list(df.index),
                             values=list(df['count']))])
    fig.update_traces(hoverinfo='label+percent', textinfo='value', textfont_size=20,
                  marker=dict(colors=colors, line=dict(color='#000000', width=2)))
    
    return fig

@app.callback(
    # Output("graph_TS","figure"),
    Output("graph_TS", "figure"),
    Input("names", "value"), 
    Input("values", "value"))
def generate_chart(names, values):
    d1=data[names][0][values]['timeSpent']
    colors = ['gold', 'mediumturquoise', 'darkorange', 'lightgreen']
    df1 = pd.DataFrame.from_dict(d1, orient='index', columns=['count']).replace('','00')
    df1['count'] = df1['count'].apply(lambda x:float(ast.literal_eval(x[:-1])))
    fig1 = go.Figure(data=[go.Pie(labels=list(df1.index),
                             values=list(df1['count']))])
    fig1.update_traces(hoverinfo='label+percent', textinfo='value', textfont_size=20,
                  marker=dict(colors=colors, line=dict(color='#000000', width=2)))
    return fig1

fig_totalTime = px.pie(timeSpent_total, values=timeSpent_total[0], names=list(timeSpent_total.index), color_discrete_sequence=px.colors.sequential.RdBu)
totalTime_pie=dcc.Graph(figure=fig_totalTime)

df1= user_data.groupby('userId').sum().apply(lambda x:x)
fig_bar_timeSpent=px.bar(df1, x=df1.index, y="timeSpent_total")
app.layout = html.Div([
    html.Div([
        html.H1('Dashboard',style={"text-align":"center"}),
    ]),
    html.Div([
        html.H5('Total Time Spent According to the users',style={"text-align":"center","margin":"20px"}),
        dcc.Graph(figure=fig_bar_timeSpent),
    ]),
        html.Div([
        html.H5('Total Time Spent by Users on total sections',style={"text-align":"center","margin":"20px"}),
        totalTime_pie,
    ]),
        html.Div([
            html.P("User ID:",style={'margin':'10px'}),
        dcc.Dropdown(id='names',
            options=data.columns,
            value=data.columns[0], clearable=False),
        html.P("Time and Date:",style={'margin':'10px'}),
        dcc.Dropdown(id='values',
            options=[],
            value="",
            clearable=False
        ),]),
    html.Div([
        html.Div([
        html.P("User's Personal Records",style={"text-align":"center","font-weight":"bold","margin-top":'20px'}),
        piePR,
        ],style={'padding': 10, 'flex': 1}),
        html.Div([
        html.P("User's Time Spent Record",style={"text-align":"center","font-weight":"bold","margin-top":'20px'}),
        pieTS,
        ],style={'padding': 10, 'flex': 1}),
        ],style={'display': 'flex', 'flex-direction': 'row'}),
        
    
    
],style={'margin':'20px','padding':'20px'})

if __name__ == '__main__':
    app.run_server(debug=True)
