from datetime import datetime
import upbit
import time
class BreakOut():
    def __init__(self):
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

    def create_buy_order(self, ticker):
        krw = float((self.upbit.get_my_account()[0])['balance']) * 0.99
        orderbook = (self.upbit.get_order_book(ticker)[0])['orderbook_units']
        lowest_price = float(orderbook[0]['ask_price']) #호가창에서 가장 저렴한 매도 가격
        unit = float(f"{(krw / lowest_price):.5f}") 
        if krw >= 5000: #최소 주문 금액
            res = self.upbit.create_order(ticker, 'bid', unit, lowest_price,"limit")
            print(f'Make Buy order at {lowest_price}, Unit: {unit}, Total Buy:{lowest_price * unit} ')
            return res
        return 
    
    def create_sell_order(self,ticker):
        orderbook = (self.upbit.get_order_book(ticker)[0])['orderbook_units']
        highest_price = float(orderbook[0]['bid_price']) #가장 비싸게 사주는 친구에게 매도
        asset = self.upbit.get_my_account()
        if len(asset) > 1: #원화를 제외한 자산이 1개 이상은 존재해야 매도가 가능하다.
            unit = float(asset[1]['balance'])
            res = self.upbit.create_order(ticker, 'ask', unit, highest_price,"limit")
            print(f'Make Sell order at {highest_price}, Unit: {unit}, Total Sell:{highest_price * unit} ')
            return res
        return 

    def run(self):
        target_price = self.get_target_price()
        sleep_sec = 30
        ticker = "KRW-BTC"
        while True:
            try:
                if self.check_reset_time():
                    target_price = self.get_target_price()
                    self.create_sell_order(ticker)
                now_price = self.upbit.get_current_price(ticker)[0]['trade_price']
                if now_price >= target_price:
                    self.create_buy_order(ticker)
                self.make_log(ticker,now_price, target_price)
                sleep_sec = 1 if abs(now_price / target_price) >= 0.99 else 30
            except Exception as e:
                print(e)
                break
            time.sleep(sleep_sec)

    def make_log(self,ticker,now_price,target_price):
        now = datetime.now()
        print(f"{now} , ticker: {ticker} target: {target_price}, now: {now_price}")
        print(f"{(now_price / target_price - 1) * 100:.2f} % from target")
        print("-" * 15)

if __name__ == "__main__":
    bot = BreakOut()    
    bot.run()




