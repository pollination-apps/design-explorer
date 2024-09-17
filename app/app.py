"""Module for app."""
import os
import dash
from dash import html, dcc, dash_table, Patch, ALL, ctx
from dash.dependencies import Input, Output, State
from pathlib import Path
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
import numpy as np
import pollination_dash_io
import base64
import zipfile
from io import BytesIO
import dash_renderjson
from pollination_io.api.client import ApiClient
from flask import send_from_directory
import time
from dash.exceptions import PreventUpdate

from containers import logo_title, info_box, hello_user, create_radio_container, \
    select_pollination_project, select_sample_project, create_color_by_container, \
    create_images_grid_children, create_images_container, create_sort_by_container
from helper import process_dataframe
from callbacks import pollination, sample, table, image
from config import base_path


app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP],
    suppress_callback_exceptions=True
)
app.title = 'Design Explorer'
server = app.server

@server.route('/pollination/<path:path>')
def serve_image(path):
    directory = Path(__file__).parent.joinpath('pollination')
    return send_from_directory(directory, path)

api_key = pollination_dash_io.ApiKey()

project_folder = 'assets/samples/daylight-factor'
csv = Path(__file__).parent.joinpath('assets', 'samples', 'daylight-factor', 'data.csv')
df = pd.read_csv(csv)
df_records = df.to_dict('records')

labels, parameters, input_columns, output_columns, image_columns = \
    process_dataframe(df)

# color by first output column, or first input column
if output_columns:
    color_by = output_columns[0]
    sort_by = output_columns[0]
else:
    color_by = input_columns[0]
    sort_by = output_columns[0]

fig = px.parallel_coordinates(df, color=color_by, labels=labels)

img_column = df.filter(regex=f'^img:').columns[0]

images_div = []
minimum, maximum = df[color_by].min(), df[color_by].max()
sorted_df = df.sort_values(by=sort_by, ascending=False)
sorted_df_records = sorted_df.to_dict('records')
images_grid_children = create_images_grid_children(
    sorted_df_records, color_by, minimum, maximum, img_column, project_folder)

columns = []
for value in parameters.values():
    if value['type'] != 'img':
        columns.append({'id': value['label'], 'name': value['display_name']})
    else:
        columns.append(
            {'id': value['label'], 'name': value['display_name'], 'hidden': True})


app.layout = dbc.Container([
    logo_title(app),
    info_box(),
    hello_user(api_key, base_path),
    create_radio_container(),
    select_sample_project(),
    select_pollination_project(),
    create_color_by_container(parameters, color_by),
    dcc.Graph(id='parallel-coordinates', figure=fig),
    create_sort_by_container(parameters, sort_by),
    create_images_container(images_grid_children),
    dcc.Store(id='project-folder', data=project_folder),
    dcc.Loading(children=[dcc.Store(id='df', data=df_records)],
        className='custom-spinner', type='default', fullscreen=True),
    dcc.Store(id='df-columns', data=df.columns),
    dcc.Store(id='labels', data=labels),
    dcc.Store(id='parameters', data=parameters),
    dcc.Store(id='img-column', data=img_column),
    dcc.Store(id='active-filters', data={}),
    dcc.Store(id='active-records', data=df_records),
    dcc.Store(id='parallel-coordinates-figure-highlight', data={}),
    dcc.Store(id='parallel-coordinates-figure', data=fig),
    dash_table.DataTable(
        id='table', data=df.to_dict('records'),
        columns=columns,
        style_table={'padding': '20px'},
        sort_action='native'),
], style={'padding': '20px'}, fluid=True)


api_key.create_api_key_callback(
    app=app,
    component_ids=['auth-user']
)


@app.callback(
    [Output(component_id='sort-ascending', component_property='data'),
     Output(component_id='button-ascending-icon', component_property='className')],
    [Input(component_id='button-ascending', component_property='n_clicks'),
     State(component_id='sort-ascending', component_property='data')],
    prevent_initial_call=True
)
def update_sort_ascending(n_clicks, sort_ascending):
    """If a click is registered in the button-ascending, the data is updated in
    sort-ascending, the className is updated in button-ascending-icon, and the
    children is updated in button-ascending-text."""
    if sort_ascending:
        return  False, 'bi bi-sort-down'
    else:
        return True, 'bi bi-sort-up'


@app.callback(
    [Output('sort-by-column', 'data'),
     Output('sort-by-dropdown', 'label')],
    [Input({'sort_by_dropdown': ALL}, 'n_clicks'),
     State('labels', 'data')],
    prevent_initial_call=True
)
def update_sort_by(n_clicks, labels):
    """If a click is registered in the sort by dropdown, the data is updated in
    sort-by-column, and the label is updated in sort-by-dropdown."""
    if all(v is None for v in n_clicks):
        return (dash.no_update,) * 2

    sort_by = ctx.triggered_id.sort_by_dropdown

    return sort_by, labels[sort_by]


@app.callback(
    [Output('parallel-coordinates', 'figure', allow_duplicate=True),
     Output('color-by-column', 'data'),
     Output('color-by-dropdown', 'label')],
    [Input({'color_by_dropdown': ALL}, 'n_clicks'),
     State('df', 'data'),
     State('labels', 'data'),
     State('parallel-coordinates', 'figure')],
    prevent_initial_call=True
)
def update_color_by(n_clicks, df_records, labels, figure):
    """If a click is registered in the color by dropdown, the figure is updated
    in parallel-coordinates, the data is updated in color-by-column, and the
    label is updated in color-by-dropdown."""
    if all(v is None for v in n_clicks):
        return (dash.no_update,) * 3

    dff = pd.DataFrame.from_records(df_records)
    color_by = ctx.triggered_id.color_by_dropdown

    if color_by:
        new_fig = Patch()
        new_fig['data'][0]['dimensions'] = figure['data'][0]['dimensions']
        new_fig['data'][0]['line']['color'] = dff[color_by]
        return new_fig, color_by, labels[color_by]
    else:
        new_fig = Patch()
        new_fig['data'][0]['dimensions'] = figure['data'][0]['dimensions']
        new_fig['data'][0]['line']['color'] = None
        return new_fig, color_by, 'None'


@app.callback(
    Output('active-records', 'data', allow_duplicate=True),
    [Input('active-filters', 'data'),
     State('df', 'data')],
    prevent_initial_call=True,
)
def update_active_records(data, df_records):
    """If the data in active-filters is changed, the data will be updated in
    active-records.
    
    The data coming from active-filters is a dictionary. Here is an example:
    {
        'In:X': [
            [3.37548768432072, 5.8024196759539395]
        ],
        'In:Z': None,
        'Out:Volume': [
            [
                [127.00292472850138, 341.43381398170953],
                [627.3416663193204, 739.2186520166465]
            ]
        ]
    }

    The keys are the column names in the DataFrame. The values are selections,
    i.e., [min, max], and one column can have multiple selections. The value can
    also be None if a selection has previously been made for this column but
    since removed.
    """
    if data:
        dff = pd.DataFrame.from_records(df_records)
        for col in data:
            if data[col]:
                # there is a selection, i.e., the value is not None
                rng = data[col][0]
                if isinstance(rng[0], list):
                    # if multiple choices combine df
                    dff3 = pd.DataFrame(columns=dff.columns)
                    for i in rng:
                        dff2 = dff[dff[col].between(i[0], i[1])]
                        dff3 = pd.concat([dff3, dff2])
                    dff = dff3
                else:
                    # there is one selection
                    dff = dff[dff[col].between(rng[0], rng[1])]
        return dff.to_dict('records')
    return dash.no_update


@app.callback(
    Output('active-filters', 'data', allow_duplicate=True),
    [Input('parallel-coordinates', 'restyleData'),
     State('df-columns', 'data')],
    prevent_initial_call=True,
)
def update_active_filters(data, df_columns):
    """If a selection is made in the parallel coordinate plot, the data will be
    updated in active-filters."""
    if data:
        key = list(data[0].keys())[0]
        col = df_columns[int(key.split('[')[1].split(']')[0])]
        new_data = Patch()
        new_data[col] = data[0][key]
        return new_data
    return dash.no_update


if __name__ == '__main__':
    app.run_server(debug=True)
