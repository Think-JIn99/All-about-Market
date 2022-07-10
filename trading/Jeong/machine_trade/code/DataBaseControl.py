from matplotlib import ticker
import pandas as pd
import author
import datetime
from ApiCaller import ApiCaller
class DataBaseControl():
    def __init__(self, db_name, ticker, interval) -> None:
        if db_name == "processed":
            self.enigne = author.processed_engine
        elif db_name == "raw":
            self.engine = author.raw_engine
        else:
            print("No DB")
            raise Exception

        self.ticker = ticker
        self.interval = interval
        self.table_name = self.create_table_name()

    def create_table_name(self):
        special_char = [':','-','/',"\\","=","^","%"]
        table_name = self.ticker
        for c in special_char:
            if c in self.ticker: 
                table_name = self.ticker.replace(c,'')

        return f"{table_name}_{self.interval}"

    def post_df(self, df):
        try:
            df = df.loc[~df.index.duplicated()]
            df.to_sql(self.table_name, self.engine, if_exists='append', index=True)
            print(self.table_name + " inserted in DB sucessfully!!")

        except Exception as e:
            print("Error occurs in post data to server")
            print(str(e))
    
    def get_df(self, *columns, table_name=None):
        try:
            columns = ','.join(columns)
            if not table_name: table_name = self.table_name
            query = f"SELECT {columns} FROM {table_name}"
            df = pd.read_sql(query, self.engine)
            df.set_index(df.columns[0], inplace=True)
            return df

        except Exception as e:
            print("Can't get data from DB")
            print(e)

    def update_table(self, table_name=None):
        if not table_name: table_name = self.table_name
        query = f"SELECT * FROM `{self.table_name}` ORDER BY Date DESC LIMIT 1;"
        now = datetime.datetime.now()
        last_date = pd.read_sql(query, con=self.engine)['Date'].iloc[-1] + datetime.timedelta(days=1) #이 다음날 부터의 데이터가 필요하다.

        if now > last_date: #하루 이상 차이가 발생하는 경우
            last_date = datetime.datetime.strftime(last_date, "%Y-%m-%d") #api호출을 위해 문자열 포맷으로 변경해준다.
            now = datetime.datetime.strftime(now, "%Y-%m-%d")
            api_caller = ApiCaller(ticker = self.ticker, interval=self.interval, start=last_date, end=now)
            ans = api_caller.run_api()
            self.post_df(ans)
        else:
            print("No need to Update")
    
    def create_table(self, start, end):
        api_caller = ApiCaller(interval=self.interval ,ticker=self.ticker, start = start, end = end)
        data = api_caller.run_api()
        self.post_df(data)


if __name__ == '__main__':
    db_control = DataBaseControl("raw","^OVX","1d")
    start = datetime.datetime(2015,2,28,0,0)
    end = datetime.datetime(2022,5,8,23,59)
    db_control.create_table(start, end)
    print(db_control.get_df("*"))