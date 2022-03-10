
import pandas as pd
class FeatureTransformer():
    def __init__(self, df):
        self.price = df['Adj Close']
        self.high = df['High']
        self.low = df['Low']
        self.volume = df['Volume']
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
        au = gains.ewm(com=period-1, min_periods=period).mean()
        ad = drops.abs().ewm(com=period-1, min_periods=period).mean()
        rs = au / ad
        rsi = pd.Series(100 - (100 / (1 + rs)))
        return rsi

    def get_vwap(self):
        volumes = self.volume
        price = self.price
        vwap = ((volumes * price).cumsum()) / volumes.cumsum()
        return vwap
    
    def get_stochastic(self, n=14, m=5):
        n_high = self.high.rolling(window=n, min_periods=1).max()
        n_low = self.low.rolling(window=n, min_periods=1).min()
        fast_k = (self.price - self.low) / (n_high - n_low) * 100
        fast_d = fast_k.ewm(span=m).mean()
        return (fast_k, fast_d)

    def transform(self):
        fast_k, fast_d = self.get_stochastic()
        macd, macd_signal = self.get_macd()
        df = pd.DataFrame({'Price': self.price, 'Gap': (self.high - self.low) / self.low,
                    'Rsi': self.get_rsi(14), 'Macd': macd, 'Macd_Signal': macd_signal,
                    'Vwap':self.get_vwap(), 'Volume':self.volume,
                    'Fast_k': fast_k,'Fast_d': fast_d})
        df.dropna(inplace=True)
        print("Create new feature complete")
        return df
