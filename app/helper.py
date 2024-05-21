"""Module with helper functions."""
import pandas as pd


def process_dataframe(df: pd.DataFrame):
    labels = {}
    parameters = {}
    input_columns = []
    output_columns = []
    image_columns = []
    for col_name, col_series in df.items():
        col_type, col_id = col_name.split(':')
        if col_type != 'img':
            labels[col_name] = col_id
            parameters[col_name] = {
                'label': col_name, 
                'display_name': col_id,
                'type': col_type
            }
            if col_type == 'in':
                input_columns.append(col_name)
            elif col_type == 'out':
                output_columns.append(col_name)
        else:
            image_columns.append(col_name)

    return labels, parameters, input_columns, output_columns, image_columns
