import datetime
import author
import yfinance as yf
import pandas as pd
class ApiCaller():
    def __init__(self, ticker, interval, start, end) -> None:
        self.ticker = ticker
        self.interval = interval
        self.start = start
        self.end = end
        
    def run_api(self):
        try:
            df = yf.download(tickers = self.ticker, interval = self.interval, start = self.start, end = self.end)
            print(f"{self.ticker}: {self.start} ~ {self.end}  is sucessfully inserted in DB")
            return df

        except:
            print("Error in get_data data can't loaded.")

# if __name__ =='__main__':
#     start = datetime.datetime(2022,2,28,0,0)
#     end = datetime.datetime(2022,5,8,23,59)
#     t = "GC=F"
#     api_caller = ApiCaller(interval="1d" ,ticker=t, start = start, end = end)
#     data = api_caller.run_api()
#     print(data)
    
