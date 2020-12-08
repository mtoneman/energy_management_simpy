import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc 
import dash_html_components as html
import plotly.express as px
import pandas as pd


app = dash.Dash('Hello World',
                external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])

#df = pd.read_csv('energy.csv')
#fig = px.line(df, x="date", y="energylevel",labels=dict(energylevel='Energy Level',date='Date'))
#fig = px.line(df, x="date", y="freshwaterlevel",labels=dict(freshwaterlevel='Fresh Water Level',date='Date'))
#fig.update_yaxes(range=[0, 100])

config = { "energylevel": { "label": "Energy Level (%)", "range": [0,100]},
           "batterylevel": { "label": "Battery Level (kWh)", "range": [0,5000]},
           "freshwaterlevel": { "label": "Fresh Water Level (l)", "range": [0,10000]}
	 }

app.layout = html.Div([
    dcc.Dropdown(
        id='my-dropdown',
        options=[
            {'label': config['energylevel']['label'], 'value': 'energylevel'},
            {'label': config['batterylevel']['label'], 'value': 'batterylevel'},
            {'label': config['freshwaterlevel']['label'], 'value': 'freshwaterlevel'}
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


#marker = dict(color = ['rgba(63, 195, 128, 1)' if x>0 else 'rgba(219, 10, 91, 1)' for x in df["percentageChange30dBtc"]], line = dict(color='rgb(0,0,0)',width=1.5)),

#
#dcc.Interval(
#            id='interval-component',
#            interval=1*1000, # in milliseconds
#            n_intervals=0


@app.callback(Output('my-graph', 'figure'), [Input('my-dropdown', 'value'),Input('interval-component', 'n_intervals')])
def update_graph(selected_dropdown_value, n_intervals):
    df = pd.read_csv('energy.csv')
    #df = pd.DataFrame(dict(market=[4, 2, 5]))
    #web.DataReader(
    #    selected_dropdown_value,
    #    'yahoo',
    #    dt(2017, 1, 1),
    #    dt.now()
    #)

    if(selected_dropdown_value == 'energylevel'):
        return {
            'data': [{
                'x': df.date,
                'y': df[selected_dropdown_value],
    	    "type": "scatter",
	    "hovertemplate": "%{x}<br>%{y}%<extra></extra>",
	    "showlegend": False,
    	    "line": {
                 #"color": "#636efa",
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
                           #"autorange": "true"
                         },
    	    }
        	#"title": {"text": "A Figure Specified By Python Dictionary"},
        }
    else:
        return {
            'data': [{
                'x': df.date,
                'y': df[selected_dropdown_value],
    	    "type": "scatter",
    	    "line": {
                 #    "color": "#636efa",
                     "width": "4",
                     "dash": "solid"
                },
            }],
            'layout': {
    	    'margin': {'l': 60, 'r': 10, 't': 20, 'b': 30},
    	    "yaxis": { 
    	               "title": { "text": config[selected_dropdown_value]['label'] },
    	               "range": config[selected_dropdown_value]['range']
                           #"autorange": "true"
                         },
    	}
    	#"title": {"text": "A Figure Specified By Python Dictionary"},
        }
 


#app.layout = html.Div([
#    dcc.Graph(figure=fig)
#], style={'width': '500'})


if __name__ == '__main__':
    app.run_server()
