"""Module for samples."""
from pathlib import Path
import pandas as pd
import plotly.express as px

from containers import create_images_grid_children
from helper import process_dataframe


sample_alias = {
    'box': {
        'id': 'box',
        'display_name': 'Box'
        },
    'box-without-img': {
        'id': 'box-without-img',
        'display_name': 'Box Without Images'
        },
    'daylight-factor': {
        'id': 'daylight-factor',
        'display_name': 'Daylight Factor'
        }
}


def load_sample_project(sample_identifier: str = sample_alias['daylight-factor']['id']):
    project_folder = f'assets/samples/{sample_identifier}'
    csv = Path(__file__).parent.joinpath('assets', 'samples', sample_identifier, 'data.csv')
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

    img_column = df.filter(regex=f'^Img:').columns[0]

    minimum, maximum = df[color_by].min(), df[color_by].max()
    sorted_df = df.sort_values(by=sort_by, ascending=False)
    sorted_df_records = sorted_df.to_dict('records')
    images_grid_children = create_images_grid_children(
        sorted_df_records, color_by, minimum, maximum, img_column, project_folder)

    columns = []
    for value in parameters.values():
        if value['type'] != 'Img':
            columns.append({'id': value['label'], 'name': value['display_name']})
        else:
            columns.append(
                {'id': value['label'], 'name': value['display_name'], 'hidden': True})

    return (parameters, color_by, fig, images_grid_children, sort_by, project_folder,
            df_records, df, labels, img_column, columns)
