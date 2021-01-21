#!/usr/bin/env python3

import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc 
import dash_html_components as html
import plotly.express as px
import pandas as pd

pathname = os.path.dirname(sys.argv[0])
DATA_DIR = f"{os.path.abspath(pathname)}/data"

app = dash.Dash('Hello World',
                external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])

config = { "energylevel": { "label": "Energy Level (%)", "range": [0,100]},
           "batterylevel": { "label": "Battery Level (kWh)", "range": [0,5000]},
           "freshwaterlevel": { "label": "Fresh Water Level (l)", "range": [0,10000]},
           "solarenergy": { "label": "Solar Power Generated (kWh)", "range": [0,50]}
	 }

app.layout = html.Div([
    dcc.Dropdown(
        id='my-dropdown',
        options=[
            {'label': config['energylevel']['label'], 'value': 'energylevel'},
            {'label': config['batterylevel']['label'], 'value': 'batterylevel'},
            {'label': config['freshwaterlevel']['label'], 'value': 'freshwaterlevel'},
            {'label': config['solarenergy']['label'], 'value': 'solarenergy'}
        ],
        value='energylevel'
    ),
    dcc.Graph(id='my-graph'),
    dcc.Interval(
         id='interval-component',
         interval=5*1000, # in milliseconds
         n_intervals=0
     )
], style={'width': '500'})



@app.callback(Output('my-graph', 'figure'), [Input('my-dropdown', 'value'),Input('interval-component', 'n_intervals')])
def update_graph(selected_dropdown_value, n_intervals):
    df = pd.read_csv(f"{DATA_DIR}/files/energy.csv")

    if(selected_dropdown_value == 'energylevel'):
        return {
            'data': [{
                'x': df.date,
                'y': df[selected_dropdown_value],
    	    "type": "scatter",
	    "hovertemplate": "%{x}<br>%{y}%<extra></extra>",
	    "showlegend": False,
    	    "line": {
                 "color": "#63da6e",
                 "width": "4",
                 "dash": "solid"
                },
            },{
                'x': df.date,
                'y': df[selected_dropdown_value].where(df[selected_dropdown_value] < 40) ,
    	    "type": "scatter",
	    "hoverinfo":"skip",
	    "showlegend": False,
    	    "line": {
                 "color": "#faa500",
                 "width": "4",
                 "dash": "solid",
    		 "outlinewidth": 0
                },
            },{
                'x': df.date,
                'y': df[selected_dropdown_value].where(df[selected_dropdown_value] < 20) ,
    	    "type": "scatter",
	    "hoverinfo":"skip",
	    "showlegend": False,
    	    "line": {
                 "color": "#f36e63",
                 "width": "4",
                 "dash": "solid",
    		 "outlinewidth": 0
                },
            }],
            'layout': {
    	    'margin': {'l': 60, 'r': 10, 't': 20, 'b': 30},
    	    "yaxis": { 
    	               "title": { "text": config[selected_dropdown_value]['label'] },
    	               "range": config[selected_dropdown_value]['range']
                         },
    	    }
        }
    elif(selected_dropdown_value == 'solarenergy'):
        return {
            'data': [{
                'x': df.date,
                'y': df[selected_dropdown_value],
    	    "type": "bar",
            }],
            'layout': {
    	    'margin': {'l': 60, 'r': 10, 't': 20, 'b': 30},
    	    "yaxis": { 
    	               "title": { "text": config[selected_dropdown_value]['label'] },
                       "autorange": "true"
                      },
    	    }
        }
    else:
         return {
            'data': [{
                'x': df.date,
                'y': df[selected_dropdown_value],
    	    "type": "scatter",
    	    "line": {
                     "width": "4",
                     "dash": "solid"
                },
            }],
            'layout': {
    	    'margin': {'l': 60, 'r': 10, 't': 20, 'b': 30},
    	    "yaxis": { 
    	               "title": { "text": config[selected_dropdown_value]['label'] },
    	               "range": config[selected_dropdown_value]['range']
                         },
    	    }
    	#"title": {"text": "A Figure Specified By Python Dictionary"},
        }
 


if __name__ == '__main__':
    app.run_server()
