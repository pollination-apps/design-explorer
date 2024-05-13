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
import zipfile
from pathlib import Path
from io import StringIO, BytesIO


def logo_title(app):
    container = html.Div(children=[
        html.Img(id='pollination-logo',
                 src=app.get_asset_url('pollination.svg'),
                 className='logo'),
        html.Span(children='Design Explorer',
                className='app-name')
    ],
    className='logo-title')
    return container


def color_parallel_coordinates(parameters, color_by):
    """Function to create the Div that contains the options for coloring the
    parallel coordinates by a column."""
    children = []
    children_input = []
    children_output = []
    for value in parameters.values():
        label = value['label']
        if value['type'] == 'In':
            children_input.append(
                dbc.DropdownMenuItem(value['display_name'],
                                     id={'color_by_dropdown': f'{label}'})
            )
        if value['type'] == 'Out':
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
        direction='end'
    )

    store = dcc.Store(id='color-by-column', data=color_by)
    color_by_label = html.Label(children='Color by', className='color-by-label')

    color_by_container = html.Div(
        className='color-by',
        id='color-by',
        children=[color_by_label, dropdown_menu, store]
    )

    return color_by_container


def sort_images(parameters, sort_by):
    """Function to create the Div that contains the options for sorting the
    images in the grid."""
    children = []
    children_input = []
    children_output = []
    for value in parameters.values():
        label = value['label']
        if value['type'] == 'In':
            children_input.append(
                dbc.DropdownMenuItem(value['display_name'],
                                     id={'sort_by_dropdown': f'{label}'})
            )
        if value['type'] == 'Out':
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
        direction='end'
    )

    sort_by_store = dcc.Store(id='sort-by-column', data=sort_by)
    button_icon = html.I(id='button-ascending-icon',
                         className='bi bi-sort-down')
    button_ascending = dbc.Button(children=[button_icon],
                                  id='button-ascending',
                                  class_name='sort-by-button')
    sort_ascending_store = dcc.Store(id='sort-ascending', data=False)
    sort_by_label = html.Label(children='Sort by',
                               id='sort-by-label',
                               className='sort-by-label')

    sort_container = html.Div(
        children=[sort_by_label, dropdown_menu, button_ascending, sort_by_store,
                  sort_ascending_store],
        className='sort-by',
        id='sort-by-div'
    )

    return sort_container


def images(images_div):
    """Function to create a Div for images."""
    images_container = html.Div([
        dcc.Store(id='selected-image-data'),
        html.Div([
            html.Div(id='selected-image-info', className='selected-image-info'),
            html.Img(id='selected-image', className='selected-image')
        ], id='selected-image-container', className='selected-image-container'),
        html.Div(children=images_div,
                 id='images-grid',
                 className='images-grid')
        ],
        id='images-grid-div', className='images'
    )

    return images_container
