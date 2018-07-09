from datetime import datetime
import pygsheets
import pandas as pd

"""
acess_data url is
https://docs.google.com/spreadsheets/d/1VEqGNyJG6BIJhyhgm7m94CjKDSLBwdS5c9AX3agiUSg/edit#gid=0
"""


def add_access_data(referrer):
    gc = pygsheets.authorize(service_file='./gspreads.json')
    # open the google spreadsheet (where 'PY to Gsheet Test' is the name of my sheet)
    wb = gc.open('access_data')
    # select the sheet "test_ex"
    ws = wb.worksheet(property='title', value="access_data")
    # get df of the sheet
    df = ws.get_as_df()

    if referrer is None:
        new_df = pd.DataFrame([['Unknown', str(datetime.utcnow())]])
    else:
        new_df = pd.DataFrame([[referrer, str(datetime.utcnow())]])

    new_df.columns = ['from_url', 'time']

    result_df = df.append(new_df)

    # #set the df to the sheet at first row on first column
    ws.set_dataframe(result_df, (1, 1))
