import datetime
import get_data
import pandas as pd
import author
import create_train_data
import sys
sys.path.insert(0,"/Users/jin/Programming/Machine_Learning/All-about-Market/trading/Jeong/machine_trade/model")
import joblib

def update_data():
    engine = author.raw_engine
    now = datetime.datetime.now()
    tickers = ['BTC-USD','QQQ','TLT','USDT-USD','DX=F','GC=F','^VIX']
    table_list = pd.read_sql("SHOW TABLES", con=engine).values.ravel()
    for t in table_list:
        query = f"SELECT * FROM `{t}` ORDER BY Date DESC LIMIT 1;"
        last_date = pd.read_sql(query, con=engine)['Date'].iloc[-1] + datetime.timedelta(days=1) #이 다음날 부터의 데이터가 필요하다.
        print(last_date)
    if now - last_date >= datetime.timedelta(days=1): #하루 이상 차이가 발생하는 경우
        last_date_ = datetime.datetime.strftime(last_date, "%Y-%m-%d") #api호출을 위해 문자열 포맷으로 변경해준다.
        now_ = datetime.datetime.strftime(now, "%Y-%m-%d")
        ans = get_data.run_api(interval='1d', engine=engine, start=last_date_, end=now, tickers=tickers)
    
    # elif int(now[-2:]) - int(last_date[-2:]) == 1:
    #     ans = get_data.run_api(interval='1d', engine=engine, tickers=tickers, period="1d")
    else:
        print("No need to Update")
        return
    
    if ans:
        print(ans)
        create_train_data.create_features()

# def update_predict():
#     engine = author.processed_engine
#     btc_model = [joblib.load("only_btc/" + n) for n in ["LassoBTCUSD_1d.pkl","RandomForestBTCUSD1d.pkl","RidgeBTCUSD_1d.pkl"]]
#     total_model = [joblib.load("total/" + n) for n in ["Lasso1d.pkl","Ridge1d.pkl","RandomForest1d.pkl"]]
#     #테이블 데이터를 합쳐서 총합 데이터 만들어 줘야함.
#     tickers = ['BTC-USD','QQQ','TLT','USDT-USD']
#     query = [f"SELECT * FROM `{t}_1d` ORDER BY Date DESC LIMIT 1;" for t in tickers]
#     df = None
    # for q in query:
        

    # btc_X = df.drop('Price',axis=1)
    # btc_y = df['Price']
    # total_X = total_df.drop('BTC_Price',axis=1)
    # total_y = total_df['BTC_Price']


if __name__ == '__main__':
    update_data()
