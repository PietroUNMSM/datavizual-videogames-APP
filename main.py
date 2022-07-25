# main.py
# =============================================================================
# common
import os
import json
from typing import List
# requirements
from dotenv import load_dotenv
import requests
import pandas as pd
from dash import Dash, html, dcc, Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import seaborn
#import matplotlib.pyplot as plt
# -----------------------------------------------------------------------------

load_dotenv('./.env')

def console_serie_info_dframe(console_serie: str, year: int) -> pd.DataFrame:
    host = os.environ['HOST_API']
    url = f'{host}/console_serie/{console_serie}/years/{year}'
    headers = {'Content-type': 'application/json'}
    
    print(f'[INFO] url: {url}')
    response = requests.get(url, headers=headers)
    data = json.loads(response.text)
    return pd.DataFrame(data)

def fig_dashboard_plots(df: pd.DataFrame) -> tuple:

    #TOP 15 DE PUBLISHERS#
    platform = Counter(df['Publisher'].tolist()).most_common(15)
    x = [x[0] for x in platform]
    y = [x[1] for x in platform]

    figTopPublishers = go.Bar(x = x,
                y = y,
                marker = dict(color = 'rgb(60, 179, 113)',
                            line=dict(color='rgb(25, 20, 20)',width=1.25)))

    layout = go.Layout()

    figTopPublishers = go.Figure(data = figTopPublishers, layout = layout)

    figTopPublishers.update_layout(title_text=f'Top 15 Publishers de VideoJuegos')


    #TOP 10 DE DEVELOPERS#
    platformDev = Counter(df['Developer'].tolist()).most_common(10)
    xDev = [xDev[0] for xDev in platformDev]
    yDev = [yDev[1] for yDev in platformDev]

    figTopDevelopers = go.Bar(x = xDev,
                y = yDev,
                marker = dict(color = 'rgba(255, 99, 71, 0.8)',
                            line=dict(color='rgb(25, 20, 20)',width=1.25)))

    layout = go.Layout()

    figTopDevelopers = go.Figure(data = figTopDevelopers, layout = layout)

    figTopDevelopers.update_layout(title_text=f'Top 10 Developers de VideoJuegos')


    #Grafico de barras para los géneros#
    fig_bv = px.bar(df, x='Genre', color='Genre', title = f'Géneros de Videjuegos')
    fig_bv

    #Grafico de barras para la clasificacion de edad#
    fig_brating = px.bar(df, x='Rating', color='Rating', title = f'Clasificación por Edad')
    fig_brating

    #Creamos una grafo de pastel de las plataformas y sus ventas#
    #Descartado temporalmente por tener libreria no compatible con JSON# 
    pie1 = go.Figure(data=[go.Pie(labels=df['Platform'], values=df["Global_Sales"], hole=.3)])
    pie1.update_layout(title_text='Ventas de las Plataformas')

    #Distribucion de Developers#
    Dist_Devs = df.groupby(pd.Grouper(key='Developer')).size().reset_index(name='count')
    figDistDevs = px.treemap(Dist_Devs, path=['Developer'], values='count')
    figDistDevs.update_layout(title_text=f'Distribución de Desarrolladores/Developers')
    figDistDevs.update_traces(textinfo="label+value")

    #Grafico de barras para los Ventas globales aportados por Publishers#
    fig_publisher = px.bar(df, y='Global_Sales', color='Publisher', title=f'Ventas Globales por Publishers')

    #Grafico de barras para los Developers#
    fig_dev = px.bar(df, y='Global_Sales', color='Developer', title=f'Ventas Globales por Developers')
    
    #Grafico de barras para los Juegos y Score de Usuarios#
    fig_users = px.bar(df, y='User_Score', color='Name', title=f'Puntuaciones de Usuarios')
    
    #Grafico de barras para los Juegos y Score de la Crítica
    fig_critic = px.bar(df, y='Critic_Score', color='Name', title=f'Puntuaciones de la Crítica')
    
    #Impacto de las clasificaciones por regiones#
    #Descartado temporalmente/NO compatible con JSON# 
    
    return figTopPublishers,figDistDevs,figTopDevelopers,fig_brating,fig_bv,pie1,fig_publisher,fig_dev,fig_users,fig_critic

# => app dashboard 
app = Dash(__name__)
server = app.server

df = console_serie_info_dframe(def_console_serie := 'playstation', def_year := 2013)
figTopPublishers,figDistDevs,figTopDevelopers,fig_brating,fig_bv,pie1,fig_publisher,fig_dev,fig_users,fig_critic = fig_dashboard_plots(df)

squared_style = {'width': '50%', 'display': 'inline-block'}
console_serie_options = [
    {'label': 'General', 'value': 'general'},
    {'label': 'PlayStation', 'value': 'playstation'},
    {'label': 'Nintendo', 'value': 'nintendo'},
    {'label': 'Microsoft', 'value': 'microsoft'},
    {'label': 'SEGA', 'value': 'sega'}
]

year_options = [1985, 1988, 1992, 1994, 1996, 1997, 1998, 1999, 2000, 2001, 2002,
       2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013,
       2014, 2015, 2016]



app.layout = html.Div(children=[
    
    html.H1(dcc.Dropdown(
        options=console_serie_options,
        value=def_console_serie, 
        id='console_serie-list'
    )),
    html.H1(dcc.Dropdown(
        options=year_options,
        value=def_year,
        id='year-list'
    )),
    html.Div(id='description', children=''),
    html.Button('Submit', id='submit-button', n_clicks=0),
    
    #GRAFOS DE DATOS
    #,,,,,,,,,,
    #dcc.Graph(id='figTopJuegos', figure=figTopJuegos),
    dcc.Graph(id='figTopPublishers', figure=figTopPublishers),
    dcc.Graph(id='figDistDevs', figure=figDistDevs),
    dcc.Graph(id='figTopDevelopers', figure=figTopDevelopers, style=squared_style),
    dcc.Graph(id='fig_brating', figure=fig_brating, style=squared_style),
    dcc.Graph(id='fig_bv', figure=fig_bv, style=squared_style),
    dcc.Graph(id='pie1', figure=pie1, style=squared_style),
    dcc.Graph(id='fig_publisher', figure=fig_publisher),
    dcc.Graph(id='fig_dev', figure=fig_dev),
    dcc.Graph(id='fig_users', figure=fig_users),
    dcc.Graph(id='fig_critic', figure=fig_critic),
    #dcc.Graph(id='figESRB', figure=figESRB)
    #figTopPublishers,figDistDevs,figTopDevelopers,fig_brating,fig_bv,pie1,fig_publisher,fig_dev,fig_users,fig_critic
    html.H3('Elaborado por Piero Yahir Curay Chacon - Julio 2022'),
])

@app.callback(    Output('description', 'children'),    Input('submit-button', 'n_clicks'),
    State('console_serie-list', 'value'),    State('year-list', 'value')) #Input --> nclicks, State --> cvalue, State --> yvalue
def update_output_descrip(n_clicks, cvalue: str, yvalue: int):
    return f'Visualización de datos para la Serie de Consolas en {cvalue.capitalize()} durante {yvalue}.'

@app.callback(
    #,,,,,,,,,,
    #Output('figTopJuegos', 'figure'),
    Output('figTopPublishers', 'figure'),
    Output('figDistDevs', 'figure'),
    Output('figTopDevelopers', 'figure'),
    Output('fig_brating', 'figure'),
    Output('fig_bv', 'figure'),
    Output('pie1', 'figure'),
    
    Output('fig_publisher', 'figure'),
    Output('fig_dev', 'figure'),
    Output('fig_users', 'figure'),
    Output('fig_critic', 'figure'),
    #Output('figESRB', 'figure'),

    Input('submit-button', 'n_clicks'),
    State('console_serie-list', 'value'),
    State('year-list', 'value')
)
def update_output_plots(n_clicks, cvalue: str, yvalue: str):
    try:
        df = console_serie_info_dframe(cvalue, yvalue)
        figTopPublishers,figDistDevs,figTopDevelopers,fig_brating,fig_bv,pie1,fig_publisher,fig_dev,fig_users,fig_critic= fig_dashboard_plots(df)
        return figTopPublishers,figDistDevs,figTopDevelopers,fig_brating,fig_bv,pie1,fig_publisher,fig_dev,fig_users,fig_critic
    except:
        return html.Div(
            html.H1('Solicitud No Disponible')
            )

if __name__ == '__main__':
    app.run_server(debug=True)
