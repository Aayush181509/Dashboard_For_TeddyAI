#importing modules 
import dash
from dash import dcc,html,dcc,html,Input,Output,Dash,State
from flask import Flask
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash
import plotly.graph_objs as go
import pandas as pd
import base64
import json
import ast
from datetime import datetime
import re
# App initialization

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

server=Flask(__name__)
app = dash.Dash(__name__,server =server,external_stylesheets=[dbc.themes.BOOTSTRAP,dbc.icons.BOOTSTRAP,external_stylesheets])
colors = {
    'background': '#111111',
    'text': '#7FDBFF'

}
# Loading the Data from a file
# global data
data=pd.read_json("/home/aayush/Documents/Otermans_Institute/data_analysis_task/data/teddyai-123ab-default-rtdb-export(2).json")[2:][['IDC']].transpose()

#Uploading Data
def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)

    try:
        if 'json' in filename:
            # Assume that the user uploaded a JSON file
            global data
            data_json = json.loads(decoded)
            data = pd.read_json(json.dumps(data_json))[2:][['IDC']].transpose()
            # print(data)
            global user_data
            global timeSpent_total
            user_data=process_data(data.T)

            timeSpent_total=pd.DataFrame(user_data.iloc[:,7:14].sum())

            # Process the data as needed
            return html.Div([
                            html.Div([
                    html.H1('Dashboard',style={"text-align":"center"}),
                ]),
                
                html.Div([
                    html.H5('Time Spent According to date:',style={"text-align":"center","margin":"20px"}),
                    html.P('Color represents user and size represents total marks by combining personal records values'),
                    dcc.Graph(figure=fig_bar_timeSpent_DateTime),
                ]),
                html.Div([
                    html.H5('Total Time( in seconds) Spent According to the users',style={"text-align":"center","margin":"20px"}),
                    dcc.Graph(figure=fig_bar_timeSpent),
                ]),
                html.Div([
                    html.Div([
                    html.H5('Total Time Spent(in seconds) by Users on total sections',style={"text-align":"center","margin":"20px"}),
                    barchart_component,
                ],style={'padding': 10, 'flex': 1}),
                html.Div([
                    html.H5('Total Time Spent by Users on total sections',style={"text-align":"center","margin":"20px"}),
                    totalTime_pie,
                ],style={'padding': 10, 'flex': 1}),
            ],style={'display': 'flex', 'flex-direction': 'row'}),
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
            ])
        else:
            return html.Div([
                'Invalid File Type'
            ])
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

@app.callback(Output('output-data-upload', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'))
def update_output(contents, filename):
    if contents is not None:
        return parse_contents(contents, filename)
    else:
        return None



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
    user_data.Date = user_data.Date.apply(date_converter)
    return user_data

def date_converter(obj):
    x=obj.replace('/','-')
    
    try:
        date_regex = re.compile(r'^\d{4}-\d{2}-\d{2}$')
        x_match = date_regex.match(x)
        if x_match:
            dt = datetime.strptime(x, '%Y-%m-%d')
        else:
            dt = datetime.strptime(x, '%d-%m-%Y')
    except ValueError:
        dt = datetime.strptime(x, '%m-%d-%Y')
        
    # Append the converted date to the output list
    return dt.strftime('%d-%m-%Y')

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

# Component 1 Barchart
barchart_component=html.Div([
    html.P("Select the data according to users: ",style={'margin':'40px'}),
    dcc.Dropdown(
        id="dropdown",
        options=list(user_data.Date.unique()),
        value=list(user_data.Date.unique())[0],
        clearable=False,
        style={"text-align":"center",'width':'200px'}
    ),
    dcc.Graph(id="graph_bar"),
])

@app.callback(
    Output("graph_bar", "figure"), 
    Input("dropdown", "value"))

def update_bar_chart(name):
    # mask=df['name']==name
    fig = px.bar(user_data[user_data.Date==name], x="Time", y="timeSpent_total", 
                 color="name")
    return fig


fig_totalTime = px.pie(timeSpent_total, values=timeSpent_total[0], names=list(timeSpent_total.index), color_discrete_sequence=px.colors.sequential.RdBu)
totalTime_pie=dcc.Graph(figure=fig_totalTime)

df1= user_data.groupby('userId').sum().apply(lambda x:x)
fig_bar_timeSpent=px.bar(df1, x=df1.index, y="timeSpent_total")

fig_bar_timeSpent_DateTime=px.scatter(user_data.sort_values('Date',ascending=False), x="Date", y=user_data.timeSpent_timeLesson,
                                      size=user_data.personalRecords_CC+user_data.personalRecords_EA+user_data.personalRecords_TCA+user_data.personalRecords_TQA,
           color='name')
app.layout = html.Div([
    html.Div([
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=False
    ),
    html.Div(id='output-data-upload'),
]),    
    
    
],style={'margin':'20px','padding':'20px'})



if __name__ == '__main__':
    app.run_server(debug=True)
