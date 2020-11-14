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


#global
df_g = pd.read_csv('./data/selected_data.csv')

df_gR = pd.read_csv('./data/reference_codes.csv')

codes = pd.read_csv('./data/un_codes.csv')

#oecd time data
df_t = pd.read_csv('./data/labor_indicators_oecd.csv')

df_tR = pd.read_csv('./data/labor_indicators_oecd.csv')

with open('./data/countries.geojson') as f:
    country_geo = json.load(f)

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
    style = {'background' : 'rgba(235, 232, 229, 1)', 'color' : 'CadetBlue', 'font-family' : 'Gill Sans, sans-serif'},
    children = [
        html.Div(
            id = 'app-container',
            style = {'display' : 'flex', 'flex-direction' : 'column', 'background' : 'rgba(235, 232, 229, 1)'},
            children = [
                html.H1(children = 'parental leave and health'),
                html.Div(
                    id = 'upper',
                    style = {
                        'display' : 'flex',
                        'flex-direction' : 'row',
                        'background_color' : 'rgba(221, 212, 202, 1)'
                    },
                    children = [
                        html.Div(
                            id = 'left-column',
                            style = {
                                'display' : 'flex',
                                'flex-direction' : 'column',
                                'background_color' : 'rgba(235, 232, 229, 1)',
                                'width' : '65%'
                            },
                            children = [
                                html.Div(
                                    id = 'selector-container',
                                    style = {'background' : 'rgba(235, 232, 229, 1)'},
                                    children = [
                                        dcc.Dropdown(
                                            id = 'metric-selection',
                                            style = {'background' : 'rgba(119, 136, 153, 0.1)'},
                                            options = [
                                                {'label' : temp.loc[i, 'indicator_name'], 'value' : temp.loc[i, 'series_code']}\
                                                for i in range(len(temp)) if 'GDP' not in temp.loc[i, 'series_code']
                                            ] + [{'label' : 'Length of paid shared parental leave (days)', 'value' : 'SH.PAR.LEVE'},
                                                {'label' : 'Length of paid maternity leave (days)', 'value' : 'SH.MMR.LEVE'}],
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
                            style = {
                                'display' : 'flex',
                                'flex-direction' : 'column',
                                'width' : '35%',
                            },
                            children = [
                                html.Div(
                                    id = 'split-container',
                                    children = [
                                        html.Div(
                                            id = 'up-split',
                                            children = [
                                                dcc.Graph(id = 'upper-g')
                                            ]
                                        ),
                                        html.Div(
                                            id = 'low-split',
                                            children = [
                                                dcc.Graph(id = 'lower-g')
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
                                html.Div(
                                    id = 'country-name',
                                    style = {
                                        'padding-left' : '10px'
                                    }
                                ),
                                html.Div(
                                    id = 'country-facts',
                                    style = {
                                        'background' : 'rgba(119, 136, 153, 0.1)',
                                        'padding-left' : '20px',
                                        'padding-right' : '10px',
                                        'padding-top' : '10px',
                                        'height' : '235px'
                                    }
                                )
                            ]
                        ),
                        html.Div(
                            id = 'lc',
                            style = {
                                'display' : 'flex',
                                'flex-direction' : 'column',
                                'width' : '45%'
                            },
                            children = [
                                html.Div(
                                    id = 'lc1',
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
                        ),
                        html.Div(
                            id = 'lr',
                            style = {
                                'display' : 'flex',
                                'flex-direction' : 'column',
                                'width' : '35%'
                            },
                            children = [
                                dcc.Dropdown(
                                    id = 'graph-selector',
                                    style = {'background' : 'rgba(119, 136, 153, 0.1)'},
                                    options = [
                                        {'label' : temp.loc[i, 'indicator_name'], 'value' : temp.loc[i, 'series_code']}
                                        for i in range(len(temp)) if not any(x in temp.loc[i, 'series_code'] for x in ['GDP', 'SG', 'SH.MMR', 'SH.PAR'])
                                    ],
                                    value = 'SP.DYN.IMRT.IN'
                                    ),
                                dcc.Graph(id = 'time-graph')
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

    trace = go.Choroplethmapbox(
                geojson = country_geo,
                locations = dff['country_code'],
                featureidkey = 'properties.ISO_A3',
                z = dff[str(year)],
                colorscale = [[0, 'rgba(146, 121, 180, 0.5)'], [1, 'rgba(95, 158, 160, 0.5)']],
                autocolorscale = False,
                colorbar = {
                    'bgcolor' : 'rgba(235, 232, 229, 1)',
                    'x' : 1
                }
    )
    return {'data' : [trace],
        'layout' : go.Layout(
            mapbox_style = 'mapbox://styles/dpfay/ckhegv94k09bc19lk7sqc8q0t',
            mapbox_accesstoken = 'pk.eyJ1IjoiZHBmYXkiLCJhIjoiY2toY2hsMmVpMDh5MDJzczJhZGQ0ZWFqZyJ9.jdNjGx-xr_KqF0aFYAoSRw',
            mapbox_zoom = 0.8,
            mapbox_center = {'lat' : 17, 'lon' : 10},
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
    Output('lfp-ed-graph', 'figure')],
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
        plot_bgcolor = 'rgba(235, 232, 229, 1)',
        paper_bgcolor = 'rgba(235, 232, 229, 1)',
        xaxis = {'visible' : False},
        yaxis = {'visible' : False},
        annotations = [{
            'text' : 'population',
            'x' : 0.955,
            'y' : 0.8,
            'showarrow' : False,
            'xanchor' : 'right',
            'yanchor' : 'bottom',
            'xref' : 'paper',
            'yref' : 'paper'
        }]
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
        plot_bgcolor = 'rgba(235, 232, 229, 1)',
        paper_bgcolor = 'rgba(235, 232, 229, 1)',
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
            plot_bgcolor = 'rgba(235, 232, 229, 1)',
            paper_bgcolor = 'rgba(235, 232, 229, 1)',
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
            plot_bgcolor = 'rgba(235, 232, 229, 1)',
            paper_bgcolor = 'rgba(235, 232, 229, 1)'
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

    return pop_fig, lab_fig, lab_ed

@app.callback(
    Output('time-graph', 'figure'),
    [Input('graph-selector', 'value'),
    Input('world-map', 'clickData')]
)
def get_timed(metric, click):
    if click is not None:
        cc = click['points'][0]['location']
        cn = codes[codes['iso'] == cc]['country'].values[0]
    else:
        cn = 'France'
        cc = 'FRA'

    dpl = df_t[df_t['Country'] == cn]
    dpl = dpl[dpl['IND'] == 'EMP18_MAT'].set_index('TIME')
    yrs = list(dpl.index)

#all deltas below have been constructed in order to place markers
#on the time-graph figure at points where policy-specific change occurred
    mat_delta = dict([])
    for i in range(len(yrs) - 1):
        a = dpl.loc[yrs[i], 'Value']
        b = dpl.loc[yrs[i+1], 'Value']
        if a != b:
            mat_delta[yrs[i+1]] = b - a

    dpl = df_t[df_t['Country'] == cn]
    dpl = dpl[dpl['IND'] == 'EMP18_PAT'].set_index('TIME')
    yrs = list(dpl.index)

    pat_delta = dict([])
    for i in range(len(yrs) - 1):
        a = dpl.loc[yrs[i], 'Value']
        b = dpl.loc[yrs[i+1], 'Value']
        if a != b:
            pat_delta[yrs[i+1]] = b - a

    dpl = df_t[df_t['Country'] == cn]
    dpl = dpl[dpl['IND'] == 'EMP18_PAR'].set_index('TIME')
    yrs = list(dpl.index)

    par_delta = dict([])
    for i in range(len(yrs) - 1):
        a = dpl.loc[yrs[i], 'Value']
        b = dpl.loc[yrs[i+1], 'Value']
        if a != b:
            par_delta[yrs[i+1]] = b - a

    dpl = df_t[df_t['Country'] == cn]
    dpl = dpl[dpl['IND'] == 'EMP18_PAID'].set_index('TIME')
    yrs = list(dpl.index)

    paid_delta = dict([])
    for i in range(len(yrs) - 1):
        a = dpl.loc[yrs[i], 'Value']
        b = dpl.loc[yrs[i+1], 'Value']
        if a != b:
            paid_delta[yrs[i+1]] = b - a

    dff = df_g[df_g['country_code'] == cc]\
        .set_index('indicator_code')\
        .drop(columns = ['country_name', 'country_code'])

    leve_delta = dict([])
    for i in range(1970, 2019):
        a = dff.loc['SH.PAR.LEVE.AL', str(i)]
        b = dff.loc['SH.PAR.LEVE.AL', str(i+1)]
        if a != b:
            leve_delta[i + 1] = b - a

    tg = go.Figure()
    tg.add_trace(go.Scatter(
        x = list(dff.loc[metric, :].index),
        y = list(dff.loc[metric, :].values),
        mode = 'lines',
        line = dict(
            width = 4,
            color = 'CadetBlue'
        )
    ))
    tg.update_layout(showlegend = False,
        plot_bgcolor = 'rgba(119, 136, 153, 0.01)',
        paper_bgcolor = 'rgba(119, 136, 153, 0.07)',
        height = 290,
        margin = {'l' : 0, 'r' : 0, 'b' : 0, 't' : 10},
        xaxis = {'visible' : True},
        yaxis = {'visible' : False},)

    return tg

@app.callback(
    [Output('upper-g', 'figure'),
    Output('lower-g', 'figure')],
    [Input('metric-selection', 'value'),
    Input('year-slider', 'value')]
)
def side_gs(metric, year):
    binaries = list(df_gR[df_gR['indicator_name'].str.contains('yes')]['series_code'])

    dff = df_g[df_g['indicator_code'] == metric]

    gdp = list(df_g[df_g['indicator_code'] == 'NY.GDP.MKTP.CD'].sort_values(by = str(year)).dropna()['country_code'])

    if metric in binaries:
        yes = list(dff[dff[str(year)] == 1]['country_code'])
        no = list(dff[dff[str(year)] == 0]['country_code'])

        yg = df_g[(df_g['indicator_code'] == 'NY.GDP.MKTP.CD') & (df_g['country_code'].isin(yes))].dropna().sort_values(by = str(year), ascending = False).reset_index(drop = True)
        ng = df_g[(df_g['indicator_code'] == 'NY.GDP.MKTP.CD') & (df_g['country_code'].isin(no))].dropna().sort_values(by = str(year), ascending = False).reset_index(drop = True)

        ug = go.Figure()
        for i in range(10):
            ug.add_trace(go.Bar(
                x = [yg.loc[i, 'country_name']],
                y = [yg.loc[i, str(year)]],
                marker_color = 'CadetBlue'
            ))

        lg = go.Figure()
        for i in range(10):
            lg.add_trace(go.Bar(
                x = [ng.loc[i, 'country_name']],
                y = [ng.loc[i, str(year)]],
                marker_color = 'rgba(146, 121, 180, 1)'
            ))

        ug.update_layout(
            annotations = [
                {'text' : 'highest GDP countries with ' \
                + ' '.join(df_gR[df_gR['series_code'] == metric]['indicator_name'].values[0].split()[2:-2]),
                'x' : 0,
                'y' : 0,
                'showarrow' : False,
                'xanchor' : 'left',
                'yanchor' : 'top',
                'xref' : 'paper',
                'yref' : 'paper'
                }
            ]
        )

        lg.update_layout(
            annotations = [
                {'text' : 'highest GDP countries without ' \
                + ' '.join(df_gR[df_gR['series_code'] == metric]['indicator_name'].values[0].split()[2:-2]),
                'x' : 0,
                'y' : 0,
                'showarrow' : False,
                'xanchor' : 'left',
                'yanchor' : 'top',
                'xref' : 'paper',
                'yref' : 'paper'
                }
            ]
        )


    else:
        top = dff[['country_name', 'country_code', str(year)]].sort_values(by = str(year), ascending = False).dropna().reset_index(drop = True)[:10]
        btm = dff[['country_name', 'country_code', str(year)]].sort_values(by = str(year)).dropna().reset_index(drop = True)[:10]

        ug = go.Figure()
        for i in range(10):
            ug.add_trace(go.Bar(
                x = [top.loc[i, 'country_name']],
                y = [top.loc[i, str(year)]],
                marker_color = 'CadetBlue'
            ))

        lg = go.Figure()
        for i in range(10):
            lg.add_trace(go.Bar(
                x = [btm.loc[i, 'country_name']],
                y = [btm.loc[i, str(year)]],
                marker_color = 'rgba(146, 121, 180, 1)'
            ))
        ug.update_layout(
            annotations = [
                {'text' : 'countries with highest ' \
                + df_gR[df_gR['series_code'] == metric]['indicator_name'].values[0].lower(),
                'x' : 0,
                'y' : 0,
                'showarrow' : False,
                'xanchor' : 'left',
                'yanchor' : 'top',
                'xref' : 'paper',
                'yref' : 'paper'
                }
            ]
        )

        lg.update_layout(
            annotations = [
                {'text' : 'countries with lowest ' \
                + df_gR[df_gR['series_code'] == metric]['indicator_name'].values[0].lower(),
                'x' : 0,
                'y' : 0,
                'showarrow' : False,
                'xanchor' : 'left',
                'yanchor' : 'top',
                'xref' : 'paper',
                'yref' : 'paper'
                }
            ]
        )



    ug.update_layout(
        showlegend = False,
        plot_bgcolor = 'rgba(235, 232, 229, 1)',
        paper_bgcolor = 'rgba(235, 232, 229, 1)',
        height = 295,
        margin = {'l' : 32, 'r' : 0, 'b' : 20, 't' : 75},
        xaxis = {'visible' : False},
        yaxis = {'visible' : False}
    )

    lg.update_layout(
        showlegend = False,
        plot_bgcolor = 'rgba(235, 232, 229, 1)',
        paper_bgcolor = 'rgba(235, 232, 229, 1)',
        height = 220,
        margin = {'l' : 32, 'r' : 0, 'b' : 20, 't' : 0},
        xaxis = {'visible' : False},
        yaxis = {'visible' : False}
    )

    return ug, lg

@app.callback(
    Output('country-facts', 'children'),
    [Input('world-map', 'clickData')]
)
def get_facts(mapclick):
    if mapclick is not None:
        cc = mapclick['points'][0]['location']
        cn = codes[codes['iso'] == cc]['country'].values[0]
    else:
        cc = 'FRA'
        cn = 'France'

    dff = df_g[df_g['country_code'] == cc]

    sys = dff[dff['indicator_code'] == 'SH.PAR.LEVE.AL']['2019'].values[0]
    mat = dff[dff['indicator_code'] == 'SH.PAR.LEVE.FE']['2019'].values[0]
    pat = dff[dff['indicator_code'] == 'SH.PAR.LEVE.MA']['2019'].values[0]

    if sys == 1:
        facts = 'As of 2019, {} had a parental leave system in place, allowing {} days of paid leave to the mother and {} days to the father.'\
            .format(cn, mat, pat)
    else:
        facts = 'As of 2019, {} did not have a national parental leave system in place.'\
            .format(cn)

    return facts

#Main
if __name__ == '__main__':
    app.run_server(debug = True)
