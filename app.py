import os
import pathlib
import re
import json
import math

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import pandas as pd
import numpy as np
from itertools import compress

import plotly.express as px
import plotly.graph_objs as go



#initialize app
app = dash.Dash(
    __name__,
    meta_tags = [
        {'name' : 'viewport'}
    ]
)
server = app.server



#load data
APP_PATH = str(pathlib.Path(__file__).parent.resolve())

#global
df_g = pd.read_csv('./data/selected_data.csv')

df_gR = pd.read_csv('./data/reference_codes.csv')

codes = pd.read_csv('./data/un_codes.csv')

#oecd
df_o = pd.read_csv(
    os.path.join(
        APP_PATH, os.path.join('data', 'parental_leave_oecd.csv')
    )
)

df_oR = pd.read_csv(
    os.path.join(
        APP_PATH, os.path.join('data', 'parental_leave_ref.csv')
    )
)

#oecd time data
df_t = pd.read_csv(
    os.path.join(
        APP_PATH, os.path.join('data', 'labor_indicators_oecd.csv')
    )
)

df_tR = pd.read_csv(
    os.path.join(
        APP_PATH, os.path.join('data', 'labor_indicators_oecd.csv')
    )
)

#with open('./data/countries.geojson') as f:
#    country_geo = json.load(f)

qs = [x for x in df_gR['series_code'] if\
    ((df_g[df_g['indicator_code'] == x]\
        .drop(columns = ['country_name', 'country_code', 'indicator_code'])\
        .isin([np.nan]).mean() < 0.6).mean() > 0.3)\
     & ('SL.TLF' not in x)\
     & ('SP.POP' not in x)\
     & ('SL.EMP' not in x)\
     & ('IC.REG' not in x)\
     & ('SL.FAM' not in x)\
     ]

qsi = [int(df_gR[df_gR['series_code'] == x].index.values) for x in qs]

temp = df_gR.iloc[qsi, :].copy().reset_index(drop = True)

#app layout
app.layout = html.Div(
    id = 'root',
    children = [
        html.Div(
            id = 'header',
            children = [
                html.H4(children = 'parental leave dashboard')
            ]
        ),
        html.Div(
            id = 'app-container',
            style = {'display' : 'flex', 'flex-direction' : 'column'},
            children = [
                html.Div(
                    id = 'upper',
                    style = {
                        'display' : 'flex',
                        'height' : '60vh'
                    },
                    children = [
                        html.Div(
                            id = 'left-column',
                            style = {
                                'display' : 'flex',
                                'flex-direction' : 'column',
                                'width' : '65%'
                            },
                            children = [
                                html.Div(
                                    id = 'selector-container',
                                    children = [
                                        dcc.Dropdown(
                                            id = 'metric-selection',
                                            options = [
                                                {'label' : temp.loc[i, 'indicator_name'], 'value' : temp.loc[i, 'series_code']}
                                                for i in range(len(temp)) if 'GDP' not in temp.loc[i, 'series_code']
                                            ],
                                            value = 'SH.PAR.LEVE.AL'
                                        ),
                                        dcc.Slider(
                                            id = 'year-slider',
                                            min = 1970,
                                            max = 2019,
                                            value = 2019,
                                            marks = {
                                                1970 : {'label' : '1970'},
                                                1975 : {'label' : '1975'},
                                                1980 : {'label' : '1980'},
                                                1985 : {'label' : '1985'},
                                                1990 : {'label' : '1990'},
                                                1995 : {'label' : '1995'},
                                                2000 : {'label' : '2000'},
                                                2005 : {'label' : '2005'},
                                                2010 : {'label' : '2010'},
                                                2015 : {'label' : '2015'}
                                                }
                                        )
                                    ]
                                ),
                                html.Div(
                                    id = 'map-container',
                                    children = [
                                        dcc.Graph(id = 'world-map')
                                    ]
                                )
                            ]
                        ),
                        html.Div(
                            id = 'right-column',
                            style = {'display' : 'flex', 'flex-direction' : 'column'},
                            children = [
                                html.Div(
                                    id = 'split-container',
                                    children = [
                                        html.Div(
                                            id = 'up-split',
                                            children = [
                                                html.P(
                                                    id = 'upper-text',
                                                    children = 'upper graph goes here'
                                                )
                                            ]
                                        ),
                                        html.Div(
                                            id = 'low-split',
                                            children = [
                                                html.P(
                                                    id = 'lower-text',
                                                    children = 'lower graph goes here'
                                                )
                                            ]
                                        )
                                    ]
                                )
                            ]
                        )
                    ]
                ),
                html.Div(
                    id = 'lower',
                    style = {
                        'display' : 'flex',
                        'flex-direction' : 'row'
                    },
                    children = [
                        html.Div(
                            id = 'll',
                            style = {
                                'display' : 'flex',
                                'flex-direction' : 'column',
                                'width' : '20%'
                            },
                            children = [
                                html.Div(id = 'country-name'),
                                html.Div(id = 'country-facts')
                            ]
                        ),
                        html.Div(
                            id = 'lc',
                            children = [
                                html.Div(
                                    id = 'lc1',
                                    style = {
                                        'display' : 'flex',
                                        'flex-direction' : 'column'
                                    },
                                    children = [
                                        dcc.Graph(id = 'population-graph')
                                    ]
                                ),
                                html.Div(
                                    id = 'lc2',
                                    children = [
                                        dcc.Graph(id = 'lfp-graph')
                                    ]
                                ),
                                html.Div(
                                    id = 'lc3',
                                    children = [
                                        dcc.Graph(id = 'lfp-ed-graph')
                                    ]
                                )
                            ]
                        )
                    ]
                )
            ]
        )
    ]
)


#Help!
years = [i for i in range(1970, 2020)]

#Create callbacks

@app.callback(
    [Output('year-slider', 'min'),
    Output('year-slider', 'max')],
    [Input('metric-selection', 'value')]
)
def slide_range(metric):
    x = list(df_g[df_g['indicator_code'] == metric]\
                .drop(columns = ['country_name', 'country_code', 'indicator_code'])\
                .isin([np.nan])
                .mean() < 1
            )
    xy = list(compress(years, x))

    return min(xy), max(xy)


@app.callback(
    Output('world-map', 'figure'),
    [Input('metric-selection', 'value'),
    Input('year-slider', 'value')]
)
def update_map(metric, year):
    dff = df_g[df_g['indicator_code'] == metric][['country_code', str(year)]]

    trace = go.Choropleth(
                locations = dff['country_code'],
                z = dff[str(year)],
                colorscale = 'RdBu',
                autocolorscale = False,
                marker_line_color = 'white'
    )
    return {'data' : [trace],
        'layout' : go.Layout(
            geo = {
                'showframe' : False,
                'projection' : {
                    'type' : 'miller'
                }
            },
            margin = {'l' : 0, 'r' : 0, 'b' : 0, 't' : 0}
        )
    }





@app.callback(
    Output('country-name', 'children'),
    [Input('world-map', 'clickData')]
)
def get_country(click):
    if click is not None:
        cc = click['points'][0]['location']
        cn = codes[codes['iso'] == cc]['country'].values[0]
    else:
        cn = 'France'

    return html.H1(cn)




@app.callback(
    [Output('population-graph', 'figure'),
    Output('lfp-graph', 'figure'),
    Output('lfp-ed-graph', 'figure'),
    Output('country-facts', 'children')],
    [Input('world-map', 'clickData'),
    Input('lfp-graph', 'clickData')]
)
def get_lab_fp(mapclick, yearclick):
    if mapclick is not None:
        cc = mapclick['points'][0]['location']
        cn = codes[codes['iso'] == cc]['country'].values[0]
    else:
        cc = 'FRA'

    if yearclick is not None:
        yr = str(yearclick['points'][0]['y'])
    else:
        yr = '2019'

    dff = df_g[df_g['country_code'] == cc].set_index('indicator_code')

    f = dff.loc['SP.POP.1564.FE.IN', yr]
    m = dff.loc['SP.POP.1564.MA.IN', yr]


    f_lab = dff.loc['SL.TLF.ACTI.FE.ZS', yr] / 100 * f
    m_lab = dff.loc['SL.TLF.ACTI.MA.ZS', yr] / 100 * m
    t_lab = f_lab + m_lab

    f_bas = dff.loc['SL.TLF.BASC.FE.ZS', yr] / 100 * f
    m_bas = dff.loc['SL.TLF.BASC.MA.ZS', yr] / 100 * m
    t_bas = f_bas + m_bas

    f_int = dff.loc['SL.TLF.INTM.FE.ZS', yr] / 100 * f
    m_int = dff.loc['SL.TLF.INTM.MA.ZS', yr] / 100 * m
    t_int = f_int + m_int

    f_adv = dff.loc['SL.TLF.ADVN.FE.ZS', yr] / 100 * f
    m_adv = dff.loc['SL.TLF.ADVN.MA.ZS', yr] / 100 * m
    t_adv = f_adv + m_adv



    tpop = dff.loc['SP.POP.TOTL', '2019']
    t14 = round(dff.loc['SP.POP.0014.TO.ZS', '2019'] / 100 * tpop)
    t65 = round(dff.loc['SP.POP.65UP.TO.ZS', '2019'] / 100 * tpop)

    f14 = dff.loc['SP.POP.0014.FE.IN', '2019']
    f64 = dff.loc['SP.POP.1564.FE.IN', '2019']
    f65 = dff.loc['SP.POP.65UP.FE.IN', '2019']

    m14 = t14 - f14
    m64 = dff.loc['SP.POP.1564.MA.IN', '2019']
    m65 = t65 - f65






    pop_fig = go.Figure()
    pop_fig.add_trace(go.Bar(
        x = [f14 / tpop],
        y = [''],
        orientation = 'h',
        marker = {'color' : 'rgba(175, 157, 200, 1)'}
        ))
    pop_fig.add_trace(go.Bar(
        x = [f64 / tpop],
        y = [''],
        orientation = 'h',
        marker = {'color' : 'rgba(146, 121, 180, 1)'}
        ))
    pop_fig.add_trace(go.Bar(
        x = [f65 / tpop],
        y = [''],
        orientation = 'h',
        marker = {'color' : 'rgba(112, 84, 150, 1)'}
        ))
    pop_fig.add_trace(go.Bar(
        x = [m14 / tpop],
        y = [''],
        orientation = 'h',
        marker = {'color' : 'rgba(118, 177, 178, 1)'}
        ))
    pop_fig.add_trace(go.Bar(
        x = [m64 / tpop],
        y = [''],
        orientation = 'h',
        marker = {'color' : 'rgba(157, 199, 200, 1)'}
        ))
    pop_fig.add_trace(go.Bar(
        x = [m65 / tpop],
        y = [''],
        orientation = 'h',
        marker = {'color' : 'rgba(183, 214, 215, 1)'}
        ))
    pop_fig.update_layout(
        height = 35,
        barmode = 'stack',
        showlegend = False,
        margin = {'l' : 32, 'r' : 0, 'b' : 0, 't' : 10},
        plot_bgcolor = 'rgba(0,0,0,0)',
        paper_bgcolor = 'rgba(0,0,0,0)',
        xaxis = {'visible' : False},
        yaxis = {'visible' : False},
        )



    p_years = [i for i in range(1970, 2020) \
        if (math.isnan(dff.loc['SP.POP.1564.FE.IN', str(i)]) == False) \
        & (math.isnan(dff.loc['SL.TLF.ACTI.FE.ZS', str(i)]) == False)]

    lab_fig = go.Figure()
    for year in p_years:

        f = dff.loc['SP.POP.1564.FE.IN', str(year)]
        m = dff.loc['SP.POP.1564.MA.IN', str(year)]

        f_lab = dff.loc['SL.TLF.ACTI.FE.ZS', str(year)] / 100 * f
        m_lab = dff.loc['SL.TLF.ACTI.MA.ZS', str(year)] / 100 * m
        t_lab = f_lab + m_lab

        lab_fig.add_trace(go.Bar(
            x = [f_lab / t_lab],
            y = [year],
            orientation = 'h',
            marker = {'color' : 'rgba(175, 157, 200, 1)'}
            ))
        lab_fig.add_trace(go.Bar(
            x = [m_lab / t_lab],
            y = [year],
            orientation = 'h',
            marker = {'color' : 'rgba(183, 214, 215, 1)'}
            ))
    lab_fig.update_layout(
        height = 250,
        barmode = 'stack',
        showlegend = False,
        plot_bgcolor = 'rgba(0,0,0,0)',
        paper_bgcolor = 'rgba(0,0,0,0)',
        margin = dict(l = 0, r = 0, t = 10, b = 0),
        xaxis = {'visible' : False},
        annotations = [{
            'text' : 'labor force participation',
            'x' : 0.955,
            'y' : 0.985,
            'showarrow' : False,
            'xanchor' : 'right',
            'yanchor' : 'bottom',
            'xref' : 'paper',
            'yref' : 'paper'
        }]
        )



    t_ed = t_bas + t_int + t_adv

    lab_ed = go.Figure()
    if math.isnan(f_bas) == False:
        lab_ed.add_trace(go.Bar(
            x = [f_bas / t_ed],
            y = [''],
            orientation = 'h',
            marker = {'color' : 'rgba(175, 157, 200, 1)'}
            ))
        lab_ed.add_trace(go.Bar(
            x = [f_int / t_ed],
            y = [''],
            orientation = 'h',
            marker = {'color' : 'rgba(175, 157, 200, 1)'}
            ))
        lab_ed.add_trace(go.Bar(
            x = [f_adv / t_ed],
            y = [''],
            orientation = 'h',
            marker = {'color' : 'rgba(175, 157, 200, 1)'}
            ))
        lab_ed.add_trace(go.Bar(
            x = [m_bas / t_ed],
            y = [''],
            orientation = 'h',
            marker = {'color' : 'rgba(183, 214, 215, 1)'}
            ))
        lab_ed.add_trace(go.Bar(
            x = [m_int / t_ed],
            y = [''],
            orientation = 'h',
            marker = {'color' : 'rgba(183, 214, 215, 1)'}
            ))
        lab_ed.add_trace(go.Bar(
            x = [m_adv / t_ed],
            y = [''],
            orientation = 'h',
            marker = {'color' : 'rgba(183, 214, 215, 1)'}
            ))
        lab_ed.update_layout(barmode = 'stack',
            showlegend = False,
            plot_bgcolor = 'rgba(0,0,0,0)',
            paper_bgcolor = 'rgba(0,0,0,0)',
            height = 35,
            margin = {'l' : 32, 'r' : 0, 'b' : 0, 't' : 10},
            xaxis = {'visible' : False},
            yaxis = {'visible' : False},
            annotations = [{
                'text' : 'labor force participation by education level',
                'x' : 0.955,
                'y' : 0.8,
                'showarrow' : False,
                'xanchor' : 'right',
                'yanchor' : 'bottom',
                'xref' : 'paper',
                'yref' : 'paper'
            }]
        )
    else:
        ch_yrs = [str(i) for i in range(1970, 2020)
            if math.isnan(dff.loc['SL.TLF.INTM.FE.ZS', str(i)]) == False]
        lab_ed.update_layout(
            xaxis = {'visible' : False},
            yaxis = {'visible' : False},
            annotations = [{
                'xref' : 'paper',
                'yref' : 'paper',
                'showarrow' : False,
                'font' : {'size' : 14}
            }],
            plot_bgcolor = 'rgba(0,0,0,0)',
            paper_bgcolor = 'rgba(0,0,0,0)'
        )
        if len(ch_yrs) > 0:
            lab_ed.update_layout(
                annotations = [{
                    'text' : "try choosing from one of the following years:<br>" + ', '.join(ch_yrs)
                }]
            )
        else:
            lab_ed.update_layout(
                annotations = [{
                    'text' : "sorry, we don't have any of this data for " + cn
                }]
            )

    return pop_fig, lab_fig, lab_ed, yr
#Main
if __name__ == '__main__':
    app.run_server(debug = True)
