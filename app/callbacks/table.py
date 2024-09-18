"""Module for table callbacks."""
import dash
from dash.dependencies import Input, Output


@dash.callback(
    Output('table', 'data', allow_duplicate=True),
    Input('active-records', 'data'),
    prevent_initial_call=True,
)
def update_table_data(active_records):
    """If the active-records is changed, the data will be updated in table."""
    return active_records
