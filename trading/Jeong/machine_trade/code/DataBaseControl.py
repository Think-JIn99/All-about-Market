from matplotlib import ticker
import pandas as pd
import author
import datetime
from ApiCaller import ApiCaller
class DataBaseControl():
    """
    class to control db table
    create_table, update_data, post_data, get_data
    """
    def __init__(self, db_name) -> None:
        if db_name == "processed":
            self.enigne = author.processed_engine
        elif db_name == "raw":
            self.engine = author.raw_engine
        else:
            print("No DB")
            raise Exception

    def create_table_name(self, ticker, interval):
        """
        create table_name. some tikcer has some special charater
        that SQL couldn't understand so use this method to remove 
        special character and create available table name.

        Args:
            ticker (str): ticker of asset
            interval (str("1d","1m"...)): interval of asset data

        Returns:
            table_name(str): available table name.
        """
        special_char = [':','-','/',"\\","=","^","%"]
        table_name = ticker
        for c in special_char:
            if c in ticker: 
                table_name = ticker.replace(c,'')

        return f"{table_name}_{interval}"

    def post_df(self, df, table_name):
        """
        post data to DB table

        Args:
            df (dataframe): data for post
            table_name (str): name of table
        """
        try:
            df = df.loc[~df.index.duplicated()]
            df.to_sql(table_name, self.engine, if_exists='append', index=True)
            print(table_name + " inserted in DB sucessfully!!")

        except Exception as e:
            print("Error occurs in post data to server")
            print(str(e))
    
    def get_df(self, *columns, table_name):
        """
        get data from table. can choose multiple columns via query

        Args:
            table_name (str): name of DB table
            columns(iterable): name of columns to get data from table

        Returns:
            df(dataframe): data from table
        """
        try:
            columns = ','.join(columns)
            query = f"SELECT {columns} FROM {table_name}"
            df = pd.read_sql(query, self.engine)
            df.set_index(df.columns[0], inplace=True)
            return df

        except Exception as e:
            print("Can't get data from DB")
            print(e)

    def update_table(self, ticker, interval):
        """
        Update data in DB tables to recent date and post data to table

        Args:
            ticker (str): ticker of asset
            interval (str("1d","1m"...)): interval of asset data
        

        """
        table_name = self.create_table_name(ticker, interval)
        query = f"SELECT * FROM `{table_name}` ORDER BY Date DESC LIMIT 1;"
        now = datetime.datetime.now()
        last_date = pd.read_sql(query, con=self.engine)['Date'].iloc[-1] + datetime.timedelta(days=1) #??? ????????? ????????? ???????????? ????????????.

        if now > last_date: #?????? ?????? ????????? ???????????? ??????
            last_date = datetime.datetime.strftime(last_date, "%Y-%m-%d") #api????????? ?????? ????????? ???????????? ???????????????.
            now = datetime.datetime.strftime(now, "%Y-%m-%d")
            api_caller = ApiCaller(ticker = ticker, interval=interval, start=last_date, end=now)
            ans = api_caller.run_api()
            self.post_df(ans, table_name)

        else:
            print("No need to Update")
    
    def create_table(self, ticker, interval, start, end):
        """
        Call yahoo api and get data after get data post it to DB

        Args:
            ticker (str): ticker of asset
            interval (str("1d","1m"...)): interval of asset data
            start (datetime): start datetime
            end (datetime): end datetime
        
        """
        api_caller = ApiCaller(interval=interval ,ticker=ticker, start = start, end = end)
        data = api_caller.run_api()
        self.post_df(data)


if __name__ == '__main__':
    db_control = DataBaseControl("raw")
    tickers = ["BTC-USD","^OVX","GC=F","^TNX","QQQ","DX=F","^VIX"]
    interval = "1d"
    for t in tickers:
        db_control.update_table(t, interval)

    # start = datetime.datetime(2015,2,28,0,0
    # end = datetime.datetime(2022,5,8,23,59)
    # db_control.create_table(start, end)
    # print(db_control.get_df("*"))
