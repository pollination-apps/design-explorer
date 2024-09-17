"""Module with function to create containers for the app layout."""
import numpy as np
import plotly.express as px
from pathlib import Path
from typing import List
from dash import html, dcc
import dash_bootstrap_components as dbc
import pollination_dash_io


def logo_title(app) -> html.Div:
    """Function to create the Div that containers the Pollination logo and app
    title (Design Explorer)."""
    container = html.Div(children=[
        html.Img(id='pollination-logo',
                 src=app.get_asset_url('pollination.svg'),
                 className='logo'),
        html.Span(children='Design Explorer (WIP)',
                className='app-name')
        ],
        className='logo-title'
    )

    return container


def info_box():
    info_box = html.Div(
        dbc.Row([
            dbc.Col(html.P(
                'This app is a work in progress. The aim is to build an app '
                'that can be used in an integrated workflow with Pollination '
                'Fly and Pollination Cloud. Check out the video on the right '
                'to see how Pollination Fly works.', className='justify-text'
            )),
            dbc.Col(html.Iframe(
                src='https://www.youtube.com/embed/X7hrUg71scE?si=o7zuXoT6B2IUdnXY'
            ))]
        ),
        className='info-box',
    )

    return info_box


def hello_user(api_key: pollination_dash_io.ApiKey, base_path: str):
    """Function to create a Div for authentication of user."""
    hello_user_container = html.Div(children=[
            html.Span(id='hello-user', children='Hi!', className='hi-user'),
            pollination_dash_io.AuthUser(id='auth-user', basePath=base_path),
            api_key.component,
        ],
        id='hello',
        className='hello'
    )
    return hello_user_container


def create_radio_container() -> html.Div:
    """Function to create the radio items."""
    container = html.Div(
        children=[
            dbc.RadioItems(
                options=[
                    {'label': 'Sample Project', 'value': False},
                    {'label': 'Load from a Pollination project (Coming soon)', 'value': True},
                ],
                value=False,
                id='radio-items-input',
                inline=True
            ),
        ],
        id='radio-items',
        className='radio-items'
    )
    return container


def select_pollination_project():
    """Function to create a Div for selecting a project on Pollination."""
    select_project_container = html.Div(children=[
        html.Div(id='select-account-container', className='pollination-dropdown'),
        html.Div(id='select-project-container', className='pollination-dropdown'),
        html.Div(id='select-artifact-container', className='pollination-dropdown')
        ],
        id='select-pollination-project',
        className='select-pollination-project'
    )

    return select_project_container


def select_sample_project() -> html.Div:
    """Function to create the Div that contains the options for coloring the
    parallel coordinates by a column."""
    children = []
    children.append(dbc.DropdownMenuItem('Daylight Factor', id={'select_sample_project': 'daylight-factor'}))
    children.append(dbc.DropdownMenuItem('Box', id={'select_sample_project': 'box'}))
    children.append(dbc.DropdownMenuItem('Box Without Images', id={'select_sample_project': 'box-without-img'}))
    dropdown_menu = dbc.DropdownMenu(
        id='select-sample-dropdown',
        label='Daylight Factor',
        children=children,
        direction='end',
        size='sm'
    )

    select_sample_label = html.Label(children='Select sample', className='color-by-label')

    select_sample_container = html.Div(
        className='select-sample',
        id='select-sample',
        children=[select_sample_label, dropdown_menu]
    )

    return select_sample_container


def create_color_by_children(parameters, color_by) -> List[html.Div]:
    """Function to create the children for the options for coloring the
    parallel coordinates by a column."""
    children = []
    children_input = []
    children_output = []
    for value in parameters.values():
        label = value['label']
        if value['type'] == 'in':
            children_input.append(
                dbc.DropdownMenuItem(value['display_name'],
                                     id={'color_by_dropdown': f'{label}'})
            )
        if value['type'] == 'out':
            children_output.append(
                dbc.DropdownMenuItem(value['display_name'],
                                     id={'color_by_dropdown': f'{label}'})
            )
    children.append(dbc.DropdownMenuItem('None', id={'color_by_dropdown': False}))
    children.append(dbc.DropdownMenuItem('Divider', divider=True))
    children.append(dbc.DropdownMenuItem('Output', header=True))
    children.extend(children_output)
    children.append(dbc.DropdownMenuItem('Divider', divider=True))
    children.append(dbc.DropdownMenuItem('Input', header=True))
    children.extend(children_input)
    dropdown_menu = dbc.DropdownMenu(
        id='color-by-dropdown',
        label=parameters[color_by]['display_name'],
        children=children,
        direction='end',
        size='sm'
    )

    store = dcc.Store(id='color-by-column', data=color_by)
    color_by_label = html.Label(children='Color by', className='color-by-label')

    children = [color_by_label, dropdown_menu, store]

    return children


def create_color_by_container(parameters, color_by) -> html.Div:
    """Function to create the Div that contains the options for coloring the
    parallel coordinates by a column."""
    children = create_color_by_children(parameters, color_by)

    color_by_container = html.Div(
        className='color-by',
        id='color-by',
        children=children
    )

    return color_by_container


def create_sort_by_children(parameters, sort_by) -> html.Div:
    """Function to create the Div that contains the options for sorting the
    images in the grid."""
    children = []
    children_input = []
    children_output = []
    for value in parameters.values():
        label = value['label']
        if value['type'] == 'in':
            children_input.append(
                dbc.DropdownMenuItem(value['display_name'],
                                     id={'sort_by_dropdown': f'{label}'})
            )
        if value['type'] == 'out':
            children_output.append(
                dbc.DropdownMenuItem(value['display_name'],
                                     id={'sort_by_dropdown': f'{label}'})
            )
    children.append(dbc.DropdownMenuItem('Output', header=True))
    children.extend(children_output)
    children.append(dbc.DropdownMenuItem('Divider', divider=True))
    children.append(dbc.DropdownMenuItem('Input', header=True))
    children.extend(children_input)
    dropdown_menu = dbc.DropdownMenu(
        id='sort-by-dropdown',
        label=parameters[sort_by]['display_name'],
        children=children,
        direction='end',
        size='sm'
    )

    sort_by_store = dcc.Store(id='sort-by-column', data=sort_by)
    button_icon = html.I(id='button-ascending-icon',
                         className='bi bi-sort-down')
    button_ascending = dbc.Button(children=[button_icon],
                                  id='button-ascending',
                                  class_name='sort-by-button',
                                  size='sm')
    sort_ascending_store = dcc.Store(id='sort-ascending', data=False)
    sort_by_label = html.Label(children='Sort by',
                               id='sort-by-label',
                               className='sort-by-label')

    children = [sort_by_label, dropdown_menu, button_ascending, sort_by_store,
                sort_ascending_store]

    return children


def create_images_grid_children(
        sorted_df_records, color_by, minimum, maximum, img_column,
        project_folder) -> List[html.Div]:
    children = []
    project_folder = Path(project_folder)
    for record in sorted_df_records:
        samplepoints = np.interp(record[color_by], [minimum, maximum], [0, 1])
        border_color = px.colors.sample_colorscale(
            'plasma', samplepoints=samplepoints
        )[0]
        src = project_folder.joinpath(record[img_column])
        image = html.Div(
            html.Img(src=src.as_posix(),
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
        children.append(image)

    return children


def create_images_container(images_div) -> html.Div:
    """Function to create a Div for images."""
    images_container = html.Div([
        dcc.Store(id='selected-image-data'),
        html.Div([
            html.Div(id='selected-image-info', className='selected-image-info'),
            html.Div(
                children=[html.Img(id='selected-image', className='selected-image')],
                id='selected-image-wrapper', className='selected-image-wrapper')
        ], id='selected-image-container', className='selected-image-container'),
        html.Div(children=images_div,
                 id='images-grid',
                 className='images-grid')
        ],
        id='images-container', className='images-container'
    )

    return images_container


def create_sort_by_container(parameters, sort_by) -> html.Div:
    """Function to create the Div that contains the options for sorting the
    images by a column."""
    children = create_sort_by_children(parameters, sort_by)
    sort_container = html.Div(
        children=children,
        className='sort-by',
        id='sort-by'
    )

    return sort_container
