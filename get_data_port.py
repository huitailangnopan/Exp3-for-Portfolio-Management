import os
import pandas as pd
import numpy as np
from math import isnan
import time
import datetime
from datetime import datetime as dx
import datetime as dt
from pytz import timezone
import csv
import pickle
import yfinance as yf

def get_data():
    '''
    content = pd.read_csv("C:\\Users\\Smart\\exp3\\123.csv")
    content = content.reset_index(drop=True)


    keep = content.loc[0]=='Close'
    for i in content.columns:
        if not keep[i]:
            content.drop(columns = i, inplace = True)
    content.dropna(axis=1)
    content = content.iloc[1:,:]
    content = content.astype(float)
    data3 = content.dropna(axis=1)
    '''


    with open("sp100tickers.pickle", "rb") as f:
                tickers = pickle.load(f)

    data =  yf.download(tickers = tickers, 
    period = "1440d", interval = "1d", group_by = 'ticker',
    auto_adjust = True,
    prepost = False,
    threads = True,
    proxy = None
    )

    data = data.loc[:, pd.IndexSlice[:, ['Close']]]

    columns = data.columns.droplevel(1)

    data.columns = columns 

    data.sort_index(axis = 1, inplace = True)
    data = data.fillna(method = "bfill")
    data = data.reset_index(drop=True)
    return data