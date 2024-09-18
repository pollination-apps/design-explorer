"""Module for records callbacks."""
import dash
from dash import Patch
from dash.dependencies import Input, Output, State
import pandas as pd


@dash.callback(
    Output('active-records', 'data', allow_duplicate=True),
    [Input('active-filters', 'data'),
     State('df', 'data')],
    prevent_initial_call=True,
)
def update_active_records(data, df_records):
    """If the data in active-filters is changed, the data will be updated in
    active-records.
    
    The data coming from active-filters is a dictionary. Here is an example:
    {
        'In:X': [
            [3.37548768432072, 5.8024196759539395]
        ],
        'In:Z': None,
        'Out:Volume': [
            [
                [127.00292472850138, 341.43381398170953],
                [627.3416663193204, 739.2186520166465]
            ]
        ]
    }

    The keys are the column names in the DataFrame. The values are selections,
    i.e., [min, max], and one column can have multiple selections. The value can
    also be None if a selection has previously been made for this column but
    since removed.
    """
    if data:
        dff = pd.DataFrame.from_records(df_records)
        for col in data:
            if data[col]:
                # there is a selection, i.e., the value is not None
                rng = data[col][0]
                if isinstance(rng[0], list):
                    # if multiple choices combine df
                    dff3 = pd.DataFrame(columns=dff.columns)
                    for i in rng:
                        dff2 = dff[dff[col].between(i[0], i[1])]
                        dff3 = pd.concat([dff3, dff2])
                    dff = dff3
                else:
                    # there is one selection
                    dff = dff[dff[col].between(rng[0], rng[1])]
        return dff.to_dict('records')
    return dash.no_update


@dash.callback(
    Output('active-filters', 'data', allow_duplicate=True),
    [Input('parallel-coordinates', 'restyleData'),
     State('df-columns', 'data')],
    prevent_initial_call=True,
)
def update_active_filters(data, df_columns):
    """If a selection is made in the parallel coordinate plot, the data will be
    updated in active-filters."""
    if data:
        key = list(data[0].keys())[0]
        col = df_columns[int(key.split('[')[1].split(']')[0])]
        new_data = Patch()
        new_data[col] = data[0][key]
        return new_data
    return dash.no_update
