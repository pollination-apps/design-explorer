"""Module for app."""
from pathlib import Path
import dash
from dash import dcc, dash_table
import dash_bootstrap_components as dbc
from flask import send_from_directory
import pollination_dash_io

from containers import logo_title, info_box, hello_user, create_radio_container, \
    select_pollination_project, select_sample_project, create_color_by_container, \
    create_images_container
from config import base_path
from samples import load_sample_project

# import callback functions
from callbacks import color, image, pollination, records, sample, sort, table


app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP],
    suppress_callback_exceptions=True
)
app.title = 'Design Explorer'
server = app.server

# this will set an alternative folder for images (alternative to "/assets")
@server.route('/pollination/<path:path>')
def serve_image(path):
    directory = Path(__file__).parent.joinpath('pollination')
    return send_from_directory(directory, path)

api_key = pollination_dash_io.ApiKey()

parameters, color_by, fig, images_grid_children, sort_by, project_folder, \
df_records, df, labels, img_column, columns = load_sample_project(
    'daylight-factor'
)

app.layout = dbc.Container([
    logo_title(app),
    info_box(),
    hello_user(api_key, base_path),
    create_radio_container(),
    select_sample_project(),
    select_pollination_project(),
    create_color_by_container(parameters, color_by),
    dcc.Graph(id='parallel-coordinates', figure=fig),
    create_images_container(images_grid_children, parameters, sort_by),
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

if __name__ == '__main__':
    app.run_server(debug=True)
