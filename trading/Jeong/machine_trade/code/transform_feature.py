import pandas as pd
class FeatureTransformer():
    def __init__(self, adj_close=None, high=None, low=None, volume=None):
        self.adj_close = adj_close
        self.high = high
        self.low = low
        self.volume = volume

    def get_macd(self):
        exp12 = self.adj_close.ewm(span = 12, adjust=False).mean()
        exp26 = self.adj_close.ewm(span = 26, adjust=False).mean()
        macd = exp12 - exp26
        signal = macd.ewm(span=9, adjust=False).mean()
        return (signal, macd)
    
    def get_stochastic(self, n=14, m=5):        
        n_high = self.high.rolling(window=n, min_periods=1).max()
        n_low = self.low.rolling(window=n, min_periods=1).min()
        fast_k = (self.adj_close - self.low) / (n_high - n_low) * 100
        fast_d = fast_k.ewm(span=m).mean()
        return (fast_k, fast_d)

    def get_rsi(self, period=14):
        delta = self.adj_close.diff()
        gains,drops = delta.copy(), delta.copy()
        gains[gains < 0] = 0
        drops[drops > 0] = 0
        au = gains.ewm(com=period - 1, min_periods=period).mean()
        ad = drops.abs().ewm(com=period - 1, min_periods=period).mean()
        rs = au / ad
        rsi = pd.Series(100 - (100 / (1 + rs)))
        return rsi

    # def get_vwap(self):
    #     volumes = self.volume
    #     adj_close = (self.adj_close + self.low + self.high) / 3
    #     vwap = ((volumes * adj_close).cumsum()) / volumes.cumsum()
    #     return vwap
    

    
    def get_pct_change(self):
        change = self.adj_close.pct_change(periods = 9)
        return change * 100

    def get_obv(self):
        # Grab the volume and close column.
        volume = self.volume
        change = self.adj_close.diff()

        # intialize the previous OBV
        prev_obv = 0
        obv_values = []

        # calculate the On Balance Volume
        for i, j in zip(change, volume):
            if i > 0:
                current_obv = prev_obv + j
            elif i < 0:
                current_obv = prev_obv - j
            else:
                current_obv = prev_obv

            # OBV.append(current_OBV)
            prev_obv = current_obv
            obv_values.append(current_obv)
        
        # Return a panda series.
        return pd.Series(obv_values, index = volume.index)

    def get_william(self,n=14):
        n_high = self.high.rolling(window=n, min_periods=1).max()
        n_low = self.low.rolling(window=n, min_periods=1).min()

        # Group by symbol, then apply the rolling function and grab the Min and Max.
        low_14 = n_low.transform(lambda x: x.rolling(window = n).min())
        high_14 = n_high.transform(lambda x: x.rolling(window = n).max())
        r_percent = ((high_14 - self.adj_close) / (high_14 - low_14)) * - 100
        return r_percent

    def get_momentum(self, is_coin=True):
        """수익률을 구해준다."""
        seed = [1]
        pct = self.adj_close.pct_change()
        pct_values = pct[1:].values.round(3)
        for i, v in enumerate(pct_values, start=1):
            seed.append(seed[i - 1] * (1 + v))

        if is_coin:
            FIRST = 14
            SECOND = 28
            THIRD = 42
        
        else:
            FIRST = 60
            SECOND = 90
            THIRD = 120

        profit = pd.Series(index=self.adj_close.index, data=seed) #profit은 실제 내 수익률을 보여준다.
        short = profit.rolling(FIRST).apply(lambda x: x.prod() ** (1.0 / FIRST)) #2주 간의 기하 평균 수익률
        mid = profit / profit.rolling(SECOND).apply(lambda x: x.prod() ** (1.0 / SECOND)) #1달 간의 기하 평균 수익률
        long = profit / profit.rolling(THIRD).apply(lambda x: x.prod() ** (1.0 / THIRD)) #2달 간의 기하 평균 수익률
        momentum = (short * 0.5 + mid * 0.3 + long * 0.2).dropna()
        return momentum

    def transform(self, df, is_coin=True): 
        #is_coin은 주식과 코인의 모멘텀을 다르게 주기 위해 사용한다.
        # self.df['Fast_k'], self.df['Fast_d'] = self.get_stochastic()
        # self.df['MACD_Signal'], self.df['MACD'] = self.get_macd()
        df['Rsi'] = self.get_rsi()
        df['Moment'] = self.get_momentum(is_coin)
        df['Pct_change'] = self.get_pct_change()
        df['OBV'] = self.get_obv()
        df['William'] = self.get_william()

        print("Create new feature complete")
        
        df.dropna(inplace=True)
        df.drop_duplicates(inplace=True)
        return df
