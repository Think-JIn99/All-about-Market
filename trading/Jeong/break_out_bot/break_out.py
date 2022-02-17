from datetime import date, datetime

from matplotlib import ticker
import upbit
import time
class BreakOut():
    def __init__(self) -> None:
        self.upbit = upbit.Upbit()

    def get_target_price(self):
        today, yesterday = self.upbit.get_day_candle('KRW-BTC','days','2')
        high = yesterday['high_price']
        low = yesterday['low_price']
        target = today['opening_price'] + (high - low) * 0.5
        return target
    
    def check_reset_time(self):
        now = datetime.now()
        return (now.hour == 9) and (now.minute == 0) and (now.second == 0)

    def create_buy_order(self, ticker, now_price, target_price):
        if now_price >= target_price:
            krw = float((self.upbit.get_my_account()[0])['balance'])
            orderbook = (self.upbit.get_order_book(ticker)[0])['orderbook_units']
            sell_price = float(orderbook[0]['ask_price']) #호가창에서 가장 저렴한 매도 가격
            unit = round((krw / sell_price),5)
        if krw >= 5000: #최소 무준 금액
            print(f'Make order at {now_price}, Unit: {unit}, Price: {sell_price}, Total Buy:{sell_price * unit} ')
            res = self.upbit.create_order(ticker, 'bid', unit, sell_price,"limit")
        return res
    
    def create_sell_order(self,ticker):
        orderbook = (self.upbit.get_order_book(ticker)[0])['orderbook_units']
        buy_price = float(orderbook[-1]['bid_price'])
        asset = self.upbit.get_my_account()
        for i,a in enumerate(asset):
            if a['currency'] == 'ticker':
                index = i
                break
        try:
            unit = asset[index]['balance']
        except Exception as e:
            print(e)
            print("No such ticker in asset")
            return

        res = self.upbit.create_order(ticker,'ask', unit, buy_price,"limit")
        return res




    def run(self):
        target_price = self.get_target_price()
        target_price = 1000
        sleep_sec = 60
        ticker = "KRW-BTC"
        while True:
            try:
                if self.check_reset_time():
                    target_price = self.get_target_price()
                    self.create_sell_order(ticker)
                now_price = self.upbit.get_current_price(ticker)[0]['trade_price']
                if now_price >= target_price:
                    self.create_buy_order(ticker, now_price, target_price)
                self.make_log(ticker,now_price, target_price)
                sleep_sec = 1 if abs(now_price / target_price) >= 0.97 else 1
            except Exception as e:
                print(e)
            time.sleep(sleep_sec)

    def make_log(self,ticker,now_price,target_price):
        now = datetime.now()
        print(f"{now} , ticker: {ticker} target: {target_price}, now: {now_price}")


bot = BreakOut()
print(bot.run())




