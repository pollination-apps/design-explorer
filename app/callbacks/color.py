"""Module for color callbacks."""
import dash
from dash import Patch, ALL, ctx
from dash.dependencies import Input, Output, State
import pandas as pd


@dash.callback(
    [Output('parallel-coordinates', 'figure', allow_duplicate=True),
     Output('color-by-column', 'data'),
     Output('color-by-dropdown', 'label')],
    [Input({'color_by_dropdown': ALL}, 'n_clicks'),
     State('df', 'data'),
     State('labels', 'data'),
     State('parallel-coordinates', 'figure')],
    prevent_initial_call=True
)
def update_color_by(n_clicks, df_records, labels, figure):
    """If a click is registered in the color by dropdown, the figure is updated
    in parallel-coordinates, the data is updated in color-by-column, and the
    label is updated in color-by-dropdown."""
    if all(v is None for v in n_clicks):
        return (dash.no_update,) * 3

    dff = pd.DataFrame.from_records(df_records)
    color_by = ctx.triggered_id.color_by_dropdown

    if color_by:
        new_fig = Patch()
        new_fig['data'][0]['dimensions'] = figure['data'][0]['dimensions']
        new_fig['data'][0]['line']['color'] = dff[color_by]
        return new_fig, color_by, labels[color_by]
    else:
        new_fig = Patch()
        new_fig['data'][0]['dimensions'] = figure['data'][0]['dimensions']
        new_fig['data'][0]['line']['color'] = None
        return new_fig, color_by, 'None'
