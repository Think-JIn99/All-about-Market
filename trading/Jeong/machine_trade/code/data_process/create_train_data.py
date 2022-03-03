from operator import index
from pandas_datareader import test
import author
import pandas as pd
import numpy as np
from functools import reduce
from sqlalchemy import create_engine
def create_new_feature(df):
    df['Gap'] = (df['High'] - df['Low']) / df['Low']
    df['RSI'] = get_rsi(df, 14)
    df['MACD'] = get_macd(df)
    df = df.dropna()
    print("Create new feature complete")
    return df

def get_macd(df):
    price = df['Adj Close']
    exp12 = price.ewm(span = 12, adjust=False).mean()
    exp26 = price.ewm(span = 26, adjust=False).mean()
    macd = exp12 - exp26
    exp = macd.ewm(span=9,adjust=False).mean()
    return exp

def get_rsi(df, period):
    close_price = df['Close']
    delta =close_price.diff()
    gains,drops = delta.copy(),delta.copy()
    gains[gains < 0] = 0
    drops[drops > 0] = 0
    au = gains.ewm(com=period-1, min_periods = period).mean()
    ad = drops.abs().ewm(com=period-1, min_periods=period).mean()
    rs = au / ad
    rsi = pd.Series(100 - (100 / (1 + rs)))
    return rsi

def merge_df(merged_df, df):
    left = merged_df
    right = create_new_feature(df) #새로 들어온 데이터 프레임을 전처리
    on_col = df.columns[0]
    merged_df = pd.merge(left,right,how='inner',on=on_col)
    return merged_df

if __name__ == '__main__':
    password = author.password
    engine = author.raw_engine
    write_engine = author.processed_engine
    test_engine = author.test_engine
    timespans = ['2m', '5m','15m', '1h', '1d']
    for timespan in timespans:
        try:
            table_list = pd.read_sql("SHOW TABLES",con=engine).values.ravel() #DB에 있는 테이블 이름을 전부 가져옴
            df_list = [pd.read_sql("SELECT * FROM {}".format(t), con = engine) for t in table_list if timespan in t]
            print("Read data from sql completed!!")
        except Exception as e:
            print("Reading Failed")
            print(str(e))
        else:
            total_df = create_new_feature(df_list[0]) #첫번째 데이터 프레임
            # for df in df_list[1:]:
            #     merged_df = merge_df(merged_df, df)

        table_name = f"total_{timespan}"
        total_df.index.name = "Date"
        total_df.to_sql(table_name, con = write_engine, if_exists='replace')