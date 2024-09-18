"""Module for sort callbacks."""
import dash
from dash import ALL, ctx
from dash.dependencies import Input, Output, State


@dash.callback(
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
        return False, 'bi bi-sort-down'
    else:
        return True, 'bi bi-sort-up'


@dash.callback(
    [Output('sort-by-column', 'data'),
     Output('sort-by-dropdown', 'label')],
    [Input({'sort_by_dropdown': ALL}, 'n_clicks'),
     State('labels', 'data')],
    prevent_initial_call=True
)
def update_sort_by(n_clicks, labels):
    """If a click is registered in the sort by dropdown, the data is updated in
    sort-by-column, and the label is updated in sort-by-dropdown."""
    if all(v is None for v in n_clicks):
        return (dash.no_update,) * 2

    sort_by = ctx.triggered_id.sort_by_dropdown

    return sort_by, labels[sort_by]
