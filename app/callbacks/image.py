"""Module for image callbacks."""
from pathlib import Path
import dash
from dash import html, ALL, ctx
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.express as px
import numpy as np


@dash.callback(
    Output('images-grid', 'children', allow_duplicate=True),
    [Input('active-records', 'data'),
     State('df', 'data'),
     Input('color-by-column', 'data'),
     Input('sort-by-column', 'data'),
     Input('sort-ascending', 'data'),
     State('img-column', 'data'),
     State('project-folder', 'data')],
    prevent_initial_call=True,
)
def update_images_grid(
        active_records, df_records, color_by_column, sort_by_column,
        sort_ascending, img_column, project_folder):
    """If the data in active-records is changed, the children will be updated
    in images-grid.
    
    The images-grid is a grid showing all the images of the selected filters in
    the parallel coordinate plot.

    The data coming from table is a list. Here is an example:
    [
        {'In:X': 1, 'In:Y': 4, 'In:Z': 3.6, 'Img:Perspective': 'X_1_Y_4_Z_3.6.png'},
        {'In:X': 2, 'In:Y': 4, 'In:Z': 3.6, 'Img:Perspective': 'X_2_Y_4_Z_3.6.png'}
    ]
    """
    if img_column is None:
        return []
    images_div = []
    if color_by_column:
        dff = pd.DataFrame.from_records(df_records)
        minimum, maximum = dff[color_by_column].min(
        ), dff[color_by_column].max()
    border_color = '#636EFA'
    if sort_by_column:
        dff = pd.DataFrame.from_records(active_records)
        sorted_df = dff.sort_values(
            by=sort_by_column, ascending=sort_ascending)
        active_records = sorted_df.to_dict('records')
    project_folder = Path(project_folder)
    for d in active_records:
        if color_by_column:
            samplepoints = np.interp(
                d[color_by_column],
                [minimum, maximum],
                [0, 1])
            border_color = px.colors.sample_colorscale(
                'plasma', samplepoints=samplepoints
            )[0]
        src = project_folder.joinpath(d[img_column])
        image = html.Div(
            html.Img(src=src.as_posix(),
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

    return images_div


@dash.callback(
    [Output('selected-image', 'src', allow_duplicate=True),
     Output('selected-image-container', 'style', allow_duplicate=True),
     Output('images-grid', 'style', allow_duplicate=True)],
    [Input('selected-image-data', 'data'),
     State('img-column', 'data'),
     State('project-folder', 'data')],
    prevent_initial_call=True,
)
def update_selected_image_table(
        selected_image_data, img_column, project_folder):
    """If the data in selected-image-table is changed.
    
    The src of selected-image is taken from selected-image-table. The styles of
    selected-image-container and images-grid are also updated."""
    if selected_image_data is None:
        return (dash.no_update,) * 3

    project_folder = Path(project_folder)
    src = project_folder.joinpath(
        selected_image_data[0][img_column]).as_posix()

    selected_image_container_style = {
        'width': '75%'
    }

    images_grid_style = {
        'grid-template-columns': 'repeat(auto-fill, minmax(10%, 1fr))',
        'width': '25%'
    }

    return src, selected_image_container_style, images_grid_style


@dash.callback(
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
        images_grid_style = {}
        return None, None, None, None, selected_image_container_style, images_grid_style


@dash.callback(
    [Output('selected-image-data', 'data', allow_duplicate=True),
     Output('selected-image-info', 'children', allow_duplicate=True)],
    [Input({'image': ALL}, 'n_clicks'),
     State('df', 'data'),
     State('labels', 'data'),
     State('img-column', 'data'),
     State('parameters', 'data')],
    prevent_initial_call=True
)
def update_clicked_image_grid(
        n_clicks, df_records, labels, img_column, parameters):
    """If a click is registered in any of the images in images-grid, the data is
    updated in selected-image-table."""
    if all(item is None for item in n_clicks):
        # no clicks, no update
        return (dash.no_update,) * 2
    # get the clicked image
    image_id = ctx.triggered_id.image
    dff = pd.DataFrame.from_records(df_records)
    selected_df = dff.loc[dff[img_column] == image_id]
    select_image_info = []
    record = selected_df.to_dict('records')
    for label in labels:
        select_image_info.append(
            html.Div(
                children=[html.Span(
                    f'{parameters[label]["display_name"]}: ',
                    className='label-bold'),
                    f'{record[0][label]}']))
    return record, select_image_info


@dash.callback(
    Output('images-container', 'style', allow_duplicate=True),
    Input('img-column', 'data'),
    prevent_initial_call=True
)
def update_images_grid_div_display(img_column):
    """If img-column is None, the display is changed to none."""
    if img_column is None:
        return {'display': 'none'}
    else:
        return {}
