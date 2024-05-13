import os
import pollination_dash_io
import dash
from dash import html, dcc, dash_table, Patch, ALL, ctx
from dash.dependencies import Input, Output, State
import dash_renderjson
from pathlib import Path
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
import numpy as np
import base64
from io import StringIO, BytesIO

from containers import logo_title, create_radio_container, \
    color_parallel_coordinates, sort_images, images

base_path = os.getenv('POLLINATION_API_URL', 'https://api.staging.pollination.cloud')

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP])
app.title = 'Design Explorer'
server = app.server

#api_key = pollination_dash_io.ApiKey()

csv = Path(__file__).parent.joinpath('assets', 'sample', 'data.csv')
df = pd.read_csv(csv)
df_records = df.to_dict('records')
dimensions = []
labels = {}
parameters = {}

input_columns = []
output_columns = []
image_columns = []
for col_name, col_series in df.items():
    col_type, col_id = col_name.split(':')
    if col_type != 'Img':
        dimension = {
            'label': col_id,
            'values': col_series.values
        }
        dimensions.append(dimension)
        labels[col_name] = col_id
        parameters[col_name] = {
            'label': col_name, 
            'display_name': col_id,
            'type': col_type
        }
        if col_type == 'In':
            input_columns.append(col_name)
        elif col_type == 'Out':
            output_columns.append(col_name)
    else:
        image_columns.append(col_name)

# color by first output column, or first input column
if output_columns:
    color_by = output_columns[0]
    sort_by = output_columns[0]
else:
    color_by = input_columns[0]
    sort_by = output_columns[0]

fig = px.parallel_coordinates(df, color=color_by, labels=labels)

img_column = df.filter(regex=f'^Img:').columns[0]

images_div = []
minimum, maximum = df[color_by].min(), df[color_by].max()
sorted_df = df.sort_values(by=sort_by, ascending=False)
sorted_df_records = sorted_df.to_dict('records')
for record in sorted_df_records:
    samplepoints = np.interp(record[color_by], [minimum, maximum], [0, 1])
    border_color = px.colors.sample_colorscale(
        'plasma', samplepoints=samplepoints
    )[0]
    image = html.Div(
        html.Img(src=f'assets/sample/{record[img_column]}',
                    id={'image': f'{record[img_column]}'},
                    className='image-grid',
                    style={'border-color': border_color}
        ),
        style={
            'aspect-ratio': '1',
            'width': '100%',
            'height': '100%',
            'position': 'relative',
            'display': 'flex',
            'align-items': 'center',
            'justify-content': 'center',
            }
    )
    images_div.append(image)

columns = []
for value in parameters.values():
    if value['type'] != 'Img':
        columns.append({'id': value['label'], 'name': value['display_name']})
    else:
        columns.append(
            {'id': value['label'], 'name': value['display_name'], 'hidden': True})


app.layout = dbc.Container([
    #api_key.component,
    logo_title(app),
    create_radio_container(),
    # pollination_dash_io.AuthUser(id='auth-user', basePath=base_path),
    # pollination_dash_io.SelectAccount(id='select-account', basePath=base_path),
    # pollination_dash_io.SelectProject(id='select-project', basePath=base_path),
    # html.Div(id='select-artifact-container'),
    #pollination_dash_io.SelectCloudArtifact(id='select-artifact', basePath=base_path),
    html.Div(id='show-temp'),
    color_parallel_coordinates(parameters, color_by),
    dcc.Store(id='df', data=df_records),
    dcc.Store(id='df-columns', data=df.columns),
    dcc.Store(id='labels', data=labels),
    dcc.Store(id='parallel-coordinates-figure', data=fig),
    dcc.Graph(id='parallel-coordinates', figure=fig),
    sort_images(parameters, sort_by),
    images(images_div),
    dash_table.DataTable(
        id='table', data=df.to_dict('records'),
        columns=columns,
        style_table={'padding': '20px'},
        sort_action='native'),
    dcc.Store(id='active-filters')
], style={'padding': '20px'}, fluid=True)


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


# api_key.create_api_key_callback(
#     app=app,
#     component_ids=['auth-user', 'select-account', 'select-project']
# )


# @app.callback(
#     Output(component_id='select-artifact', component_property='projectName'),
#     Input(component_id='select-project', component_property='project'),
#     prevent_initial_call=True
# )
# def update_select_artifact_project_name(project):
#     """If project in select-project is changed, the projectName in
#     select-artifact is updated."""
#     if project is None:
#         return None
#     return project['name']

# @app.callback(
#     Output('csv', 'data', allow_duplicate=True),
#     [Input('select-artifact', 'value'),
#      State('select-artifact', 'projectOwner'),
#      State('select-project', 'project')],
#     prevent_initial_call=True
# )
# def get_dataframe_from_csv(value, project_owner, project):
#     decoded_bytes = base64.b64decode(value)
#     csv_data = BytesIO(decoded_bytes)
#     new_df = pd.read_csv(csv_data)
#     #print(new_df)
#     print(project['id'], project['owner']['id'])
#     Path(__file__).parent.joinpath('assets', 'sample', 'data.csv')
#     return None


# @app.callback(
#     Output(component_id='select-artifact-container', component_property='children'),
#     [Input(component_id='select-project', component_property='project'),
#      State(component_id='auth-user', component_property='apiKey')],
#     prevent_initial_call=True
# )
# def update_select_artifact_project_name(project, api_key):
#     """If project in select-project is changed, the projectName in
#     select-artifact is updated."""
#     if project is None:
#         return None
#     project_owner = project['owner']['name']
#     project_name = project['name']
#     print(project_owner, project_name, api_key)
#     select_cloud_artifact = \
#         pollination_dash_io.SelectCloudArtifact(id='select-artifact',
#                                                 projectOwner=project_owner,
#                                                 projectName=project_name,
#                                                 basePath=base_path,
#                                                 apiKey=api_key)
#     api_client = pollination_io.api.client.ApiClient(host=base_path, api_token=api_key)

#     return select_cloud_artifact


# @app.callback(
#     Output(component_id='select-project', component_property='projectOwner'),
#     Input(component_id='select-account', component_property='account'),
#     prevent_initial_call=True
# )
# def update_project_owner(account):
#     """If account in select-account is changed, the projectOwner is updated in
#     select-project and select-artifact."""
#     project_owner = account.get('account_name') or account.get('username')
#     return project_owner

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
    sort_by = ctx.triggered_id.sort_by_dropdown

    return sort_by, labels[sort_by]


@app.callback(
    [Output('parallel-coordinates', 'figure'),
     Output('color-by-column', 'data'),
     Output('color-by-dropdown', 'label')],
    [Input({'color_by_dropdown': ALL}, 'n_clicks'),
     State('df', 'data'),
     State('labels', 'data')],
    prevent_initial_call=True
)
def update_color_by(n_clicks, df_records, labels):
    """If a click is registered in the color by dropdown, the figure is updated
    in parallel-coordinates, the data is updated in color-by-column, and the
    label is updated in color-by-dropdown."""
    dff = pd.DataFrame.from_records(df_records)
    color_by = ctx.triggered_id.color_by_dropdown
    if color_by:
        new_fig = px.parallel_coordinates(
            dff, color=color_by, labels=labels,
            color_continuous_scale=px.colors.get_colorscale('plasma'))
        return new_fig, color_by, labels[color_by]
    else:
        new_fig = px.parallel_coordinates(
            dff, labels=labels,
            color_continuous_scale=px.colors.get_colorscale('plasma'))
        return new_fig, color_by, 'None'


@app.callback(
    [Output('selected-image-data', 'data'),
     Output('selected-image-info', 'children')],
    [Input({'image': ALL}, 'n_clicks'),
     State('labels', 'data')],
    prevent_initial_call=True
)
def update_clicked_image_grid(n_clicks, labels):
    """If a click is registered in any of the images in images-grid, the data is
    updated in selected-image-table."""
    if all(item is None for item in n_clicks):
        # no clicks, no update
        return dash.no_update
    # get the clicked image
    image_id = ctx.triggered_id.image
    selected_df = df.loc[df[img_column] == image_id]
    select_image_info = []
    records = selected_df.to_dict('records')
    for label in labels:
        select_image_info.append(
            html.Div(children=[
                html.Span(f'{parameters[label]["display_name"]}: ', className='label-bold'),
                f'{records[0][label]}'
                ])
        )
    return records, select_image_info


@app.callback(
    [Output('selected-image', 'src', allow_duplicate=True),
     Output('selected-image', 'n_clicks', allow_duplicate=True),
     Output('selected-image-data', 'data', allow_duplicate=True),
     Output('selected-image-info', 'children', allow_duplicate=True),
     Output('selected-image-container', 'style', allow_duplicate=True),
     Output('images-grid', 'style', allow_duplicate=True)],
    Input('selected-image', 'n_clicks'),
    prevent_initial_call=True
)
def update_click_selected_image(n_clicks):
    """If a click is registered on selected-image.
    
    When this happens we reset everything related to the selected-image. The
    style of images-grid is also reset to its original state."""
    if n_clicks is not None:
        selected_image_container_style = {}
        image_grid_style = {}
        return None, None, None, None, selected_image_container_style, image_grid_style


@app.callback(
    [Output('selected-image', 'src', allow_duplicate=True),
     Output('selected-image-container', 'style', allow_duplicate=True),
     Output('images-grid', 'style', allow_duplicate=True)],
    Input('selected-image-data', 'data'),
    prevent_initial_call=True,
)
def update_selected_image_table(selected_image_data):
    """If the data in selected-image-table is changed.
    
    The src of selected-image is taken from selected-image-table. The styles of
    selected-image-container and images-grid are also updated."""
    if selected_image_data is None:
        return dash.no_update

    src = f'assets/sample/{selected_image_data[0][img_column]}'

    # create the style for selected-image-container
    selected_image_container_style = {
        'width': '75%'
    }

    # create the style for images-grid
    image_grid_style = {
        'grid-template-columns': 'repeat(auto-fill, minmax(10%, 1fr))',
        'width': '25%'
    }

    return src, selected_image_container_style, image_grid_style


@app.callback(
    [Output('images-grid', 'children', allow_duplicate=True),
     Output('images-grid', 'style', allow_duplicate=True)],
    [Input('table', 'data'),
     State('selected-image-data', 'data'),
     State('df', 'data'),
     Input('color-by-column', 'data'),
     Input('sort-by-column', 'data'),
     Input('sort-ascending', 'data')],
    prevent_initial_call=True,
)
def update_image_grid(
        data, selected_image_data, df_records, color_by_column, sort_by_column,
        sort_ascending):
    """If the data in table is changed, the children and style will be updated
    in images-grid.
    
    The images-grid is a grid showing all the images of the selected filters in
    the parallel coordinate plot.

    The data coming from table is a list. Here is an example:
    [
        {'In:X': 1, 'In:Y': 4, 'In:Z': 3.6, 'Img:Perspective': 'X_1_Y_4_Z_3.6.png'},
        {'In:X': 2, 'In:Y': 4, 'In:Z': 3.6, 'Img:Perspective': 'X_2_Y_4_Z_3.6.png'}
    ]
    """
    images_div = []
    if color_by_column:
        dff = pd.DataFrame.from_records(df_records)
        minimum, maximum = dff[color_by_column].min(), dff[color_by_column].max()
    border_color = '#636EFA'
    if sort_by_column:
        dff = pd.DataFrame.from_records(data)
        sorted_df = dff.sort_values(by=sort_by_column, ascending=sort_ascending)
        data = sorted_df.to_dict('records')
    for d in data:
        if color_by_column:
            samplepoints = np.interp(d[color_by_column], [minimum, maximum], [0, 1])
            border_color = px.colors.sample_colorscale(
                'plasma', samplepoints=samplepoints
            )[0]
        image = html.Div(
            html.Img(src=f'assets/sample/{d[img_column]}',
                     id={'image': f'{d[img_column]}'},
                     className='image-grid',
                     style={'border-color': border_color}
            ),
            style={
                'aspect-ratio': '1',
                'width': '100%',
                'height': '100%',
                'position': 'relative',
                'display': 'flex',
                'align-items': 'center',
                'justify-content': 'center',
                }
        )
        images_div.append(image)

    if selected_image_data:
        image_grid_style = {
            'grid-template-columns': 'repeat(auto-fill, minmax(10%, 1fr))',
            'width': '25%'
        }
    else:
        image_grid_style = {}

    return images_div, image_grid_style


@app.callback(
    Output('table', 'data', allow_duplicate=True),
    [Input('parallel-coordinates', 'figure'),
     State('df', 'data')],
    prevent_initial_call=True,
)
def update_table_from_figure(figure, df_records):
    """If the figure in parallel-coordinates is changed, the data in table will
    be updated (reset to default)."""
    return df_records


@app.callback(
    Output('table', 'data', allow_duplicate=True),
    [Input('active-filters', 'data'),
     State('df', 'data')],
    prevent_initial_call=True,
)
def update_table(data, df_records):
    """If the data in active-filters is changed, the data will be updated in
    table.
    
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
    return df_records


@app.callback(
    Output('active-filters', 'data'),
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
        new_data = {}
        new_data[col] = data[0][key]
        return new_data
    return {}


if __name__ == '__main__':
    app.run_server(debug=True)
