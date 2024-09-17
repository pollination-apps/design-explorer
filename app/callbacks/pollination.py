import dash
from dash.dependencies import Input, Output, State
from pathlib import Path
import pandas as pd
import plotly.express as px
import pollination_dash_io
import base64
import zipfile
from io import BytesIO
from dash.exceptions import PreventUpdate

from containers import create_color_by_children, create_sort_by_children
from helper import process_dataframe
from config import pollination_path, base_path


@dash.callback(
    Output('select-artifact-container', 'children'),
    [Input('select-project', 'project'),
     State('auth-user', 'apiKey')],
    prevent_initial_call=True
)
def update_select_artifact_container(project, apiKey):
    """Function to change the children of select-artifact-container."""
    if project is None:
        return dash.no_update
    project_owner = project['owner']['name']
    project_name = project['name']
    select_cloud_artifact = pollination_dash_io.SelectCloudArtifact(
        id='select-artifact', projectOwner=project_owner,
        projectName=project_name, basePath=base_path,
        apiKey=apiKey, fileNameMatch='.zip')

    return select_cloud_artifact


@dash.callback(
    Output('select-project-container', 'children'),
    [Input('select-account', 'account'),
     State('auth-user', 'apiKey')],
    prevent_initial_call=True
)
def update_select_project_container(account, apiKey):
    """Function to change the children of select-project-container."""
    if account is None:
        return dash.no_update
    project_owner = account.get('account_name') or account.get('username')
    select_project = pollination_dash_io.SelectProject(
        id='select-project', projectOwner=project_owner, basePath=base_path,
        apiKey=apiKey)
    return select_project


@dash.callback(
    [Output('select-account-container', 'children'),
     Output('select-sample', 'style'),
     Output('select-pollination-project', 'style')],
    [Input('radio-items-input', 'value'),
     State('auth-user', 'apiKey')],
    prevent_initial_call=True
)
def update_select_account_container(value, apiKey):
    """Function to change the children of select-account-container."""
    if value:
        select_cloud_artifact = pollination_dash_io.SelectAccount(
            id='select-account', basePath=base_path,
            apiKey=apiKey)
        return select_cloud_artifact, {'display': 'none'}, {'display': 'flex'}
    else:
        return dash.no_update, {}, {'display': 'none'}


@dash.callback(
    [Output('project-folder', 'data', allow_duplicate=True),
     Output('df', 'data', allow_duplicate=True),
     Output('active-records', 'data', allow_duplicate=True),
     Output('active-filters', 'data', allow_duplicate=True),
     Output('df-columns', 'data', allow_duplicate=True),
     Output('labels', 'data', allow_duplicate=True),
     Output('img-column', 'data', allow_duplicate=True),
     Output('parameters', 'data', allow_duplicate=True),
     Output('parallel-coordinates', 'figure', allow_duplicate=True),
     Output('sort-by', 'children', allow_duplicate=True),
     Output('color-by', 'children', allow_duplicate=True),
     Output('table', 'columns', allow_duplicate=True),
     Output('selected-image-info', 'children', allow_duplicate=True),
     Output('selected-image-container', 'style', allow_duplicate=True),
     Output('images-grid', 'style', allow_duplicate=True),
     Output('images-container', 'style')],
    [Input('select-artifact', 'value'),
     Input('select-artifact', 'name'),
     Input('select-artifact', 'key'),
     State('select-project', 'project')],
    prevent_initial_call=True
)
def load_project_from_pollination(value, name, key, project):
    if value is None or name is None or key is None:
        raise PreventUpdate

    bytes_value = base64.b64decode(value)
    file = Path(name)
    zip_file_like = BytesIO(bytes_value)
    output_folder = pollination_path.joinpath(
        project['owner']['id'], project['id'], file.stem)
    project_folder = f'pollination/{project["owner"]["id"]}/{project["id"]}/{file.stem}'
    with zipfile.ZipFile(zip_file_like, 'r') as zip_file:
        zip_file.extractall(output_folder)
    csv_file = output_folder.joinpath('data.csv')
    assert csv_file.exists(), 'File data.csv does not exists in zip file.'
    dff = pd.read_csv(csv_file)
    df_records = dff.to_dict('records')

    labels, parameters, input_columns, output_columns, image_columns = \
        process_dataframe(dff)

    if output_columns:
        color_by = output_columns[0]
        sort_by = output_columns[0]
    else:
        color_by = input_columns[0]
        sort_by = output_columns[0]

    fig = px.parallel_coordinates(dff, color=color_by, labels=labels)

    img_column = dff.filter(regex=f'^img:').columns[0]

    columns = []
    for value in parameters.values():
        if value['type'] != 'img':
            columns.append(
                {'id': value['label'],
                 'name': value['display_name']})
        else:
            columns.append(
                {'id': value['label'],
                 'name': value['display_name'],
                 'hidden': True})

    sort_by_children = create_sort_by_children(parameters, sort_by)
    color_by_children = create_color_by_children(parameters, color_by)

    active_filters = {}
    selected_image_info = None
    selected_image_container_style = {}
    image_grid_style = {}

    return (project_folder, df_records, df_records, active_filters, dff.columns,
            labels, img_column, parameters, fig, sort_by_children,
            color_by_children, columns, selected_image_info,
            selected_image_container_style, image_grid_style, {})
