import pandas as pd
class FeatureTransformer():
    def __init__(self, df):
        self.price = df['Adj Close']
        self.high = df['High']
        self.low = df['Low']
        self.volume = df['Volume']
        self.pct = df['Adj Close'].pct_change()
        return

    def get_macd(self):
        price = self.price
        exp12 = price.ewm(span = 12, adjust=False).mean()
        exp26 = price.ewm(span = 26, adjust=False).mean()
        macd = exp12 - exp26
        signal = macd.ewm(span=9, adjust=False).mean()
        return signal, macd

    def get_rsi(self, period=14):
        close_price = self.price
        delta = close_price.diff()
        gains,drops = delta.copy(), delta.copy()
        gains[gains < 0] = 0
        drops[drops > 0] = 0
        au = gains.ewm(com=period - 1, min_periods=period).mean()
        ad = drops.abs().ewm(com=period - 1, min_periods=period).mean()
        rs = au / ad
        rsi = pd.Series(100 - (100 / (1 + rs)))
        return rsi

    def get_vwap(self):
        volumes = self.volume
        price = (self.price + self.low + self.high) / 3
        vwap = ((volumes * price).cumsum()) / volumes.cumsum()
        return vwap
    
    def get_stochastic(self, n=14, m=5):
        n_high = self.high.rolling(window=n, min_periods=1).max()
        n_low = self.low.rolling(window=n, min_periods=1).min()
        fast_k = (self.price - self.low) / (n_high - n_low) * 100
        fast_d = fast_k.ewm(span=m).mean()
        return (fast_k, fast_d)
    
    def get_momentum(self, is_coin=True):
        """수익률을 구해준다."""
        seed = [1]
        pct_values = self.pct[1:].values.round(3)
        for i, v in enumerate(pct_values, start=1):
            seed.append(seed[i - 1] * (1 + v))

        if is_coin:
            FIRST = 14
            SECOND = 30
            THIRD = 60
        else:
            FIRST = 60
            SECOND = 90
            THIRD = 180

        profit = pd.Series(index=self.price.index, data=seed) #profit은 실제 내 수익률을 보여준다.
        short = profit.rolling(FIRST).apply(lambda x: x.prod() ** (1.0 / FIRST)) #2주 간의 기하 평균 수익률
        mid = profit / profit.rolling(SECOND).apply(lambda x: x.prod() ** (1.0 / SECOND)) #1달 간의 기하 평균 수익률
        long = profit / profit.rolling(THIRD).apply(lambda x: x.prod() ** (1.0 / THIRD)) #2달 간의 기하 평균 수익률
        momentum = (short * 0.5 + mid * 0.3 + long * 0.2).dropna()
        return momentum

    def process_feature(self, df):
        volume_mva = df['Volume'].rolling(window = 7).mean()
        df['Volume'] = df['Volume'] / volume_mva
        df['Pct'] = df['Price'].pct_change() * 100
        df = df.apply(lambda x: x.round(3)) #적당히 값을 묶어주기 위해 소수점 3자리를 기점으로 반올림을 진행한다.
        df.dropna(inplace=True)
        return df

    def transform(self, is_coin=True): 
        #is_coin은 주식과 코인의 모멘텀을 다르게 주기 위해 사용한다.
        fast_k, fast_d = self.get_stochastic()
        macd, macd_signal = self.get_macd()
        df = pd.DataFrame({'Price': self.price, 'Gap': (self.high - self.low) / self.low,
                    'Rsi': self.get_rsi(14), 'Macd': macd, 'Macd_Signal': macd_signal,
                    'Vwap':self.get_vwap(), 'Volume':self.volume,
                    'Fast_k': fast_k,'Fast_d': fast_d, 'Moment': self.get_momentum(is_coin), 'Pct':self.pct})
        print("Create new feature complete")
        processed_df = self.process_feature(df)
        return processed_df
