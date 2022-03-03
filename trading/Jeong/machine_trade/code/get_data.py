import datetime
from operator import index
from os import pread
import author
import yfinance as yf
import time
import pandas as pd
from sqlalchemy import create_engine

def get_data(ticker, interval, start = None, end = None, period = None):
    df = pd.DataFrame({})
    if period:
        df = yf.download(tickers = ticker, interval = interval, period=period)
        return df
    
    period = datetime.timedelta(days=6) if (interval != '1d') else datetime.timedelta(days=30)
    now_date = start

    while now_date <= end:
        try:
            end_ = now_date + period if (end > now_date + period) else end 
            data = yf.download(tickers = ticker, interval = interval, start = now_date, end = end_)
            print(f"{ticker}: {now_date} ~ {now_date + period}, now: {datetime.datetime.now()}")
            df = pd.concat([df,data])
            now_date += period
        except Exception as e:
            time.sleep(3)
            print(str(e))
    return df

def post_sql(df, ticker, interval , engine):
    special_char = [':','-','/',"\\"]
    for c in special_char:
        if c in ticker:
            ticker = ticker.replace(c,'')
    table_name = f'{ticker}_{interval}'
    try:
        # df.index.name = 'Date'
        df.to_sql(table_name, engine, if_exists='replace')
        print(table_name + " inserted in DB sucessfully!!")

    except Exception as e:
        print(str(e))
    
    return

def run_api(interval, engine, start = None, end = None, tickers = ['QQQ','BTC-USD','TLT'], period = None):
    for t in tickers:
        if period:
            df = get_data(ticker = t, interval = interval, period = period)
        else:
            df = get_data(ticker = t, interval = interval, start = start, end = end)
        print(df)
        post_sql(df, t, interval, engine)
        print(t + "_" + interval + ' is sucessfully inserted in DB')
    print('*' * 25)


if __name__ =='__main__':
    engine = author.raw_engine
    start_1m = datetime.datetime(2021,12,31,0,0)
    end_1m = datetime.datetime(2022,3,1,23,59)
    run_api("1m", engine ,start = start_1m, end = end_1m, tickers=['BTC-USD'])

    # run_api("2m",engine,tickers=['BTC-USD'],period='1mo')
    # run_api("15m",engine,tickers=['BTC-USD'],period='1mo')



    # start_1h = datetime.datetime(2020,2,23,0,0)
    # end_1h = datetime.datetime(2022,2,26,23,59)
    # run_api("1h", start_1h, end_1h, engine)


    # start_day = datetime.datetime(2019,12,1,0,0)
    # end_day = datetime.datetime(2022,2,26,23,59)
    # run_api("1d", start_day, end_day)

    # engine = author.test_engine
    # bull_start = datetime.datetime(2020,12,1,0,0)
    # bull_end = datetime.datetime(2021,4,1,23,59)
    # run_api('1h', bull_start, bull_end, engine)