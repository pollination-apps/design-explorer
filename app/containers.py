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
