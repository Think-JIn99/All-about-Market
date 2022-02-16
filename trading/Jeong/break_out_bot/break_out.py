from datetime import date, datetime
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
    
    def check_mid_night(self):
        now = datetime.now()
        return (now.hour == 0) and (now.minute == 0) and (now.second == 0) 
    
    def run(self):
        target_price = self.get_target_price()
        while True:
            try:
                if self.check_mid_night():
                    target_price = self.get_target_price()
                now_price = self.upbit.get_current_price('KRW-BTC')[0]['trade_price']
                if now_price >= target_price:
                    krw = (self.upbit.get_my_account()[0])['balance']
                    orderbook = self.upbit.get_order_book()['orderbook_units']
                    sell_price = orderbook[0]['ask_price'] #호가창에서 가장 저렴한 매도 가격
                    unit = krw / sell_price
                    if krw > 5000:
                        self.upbit.make_order('KRW-BTC', unit, sell_price)
                self.make_log(now_price, target_price)
            except Exception as e:
                print(e)
            time.sleep(1)

    def make_log(self,now_price,target_price):
        now = datetime.now()
        print(f"{now} , target: {target_price}, now: {now_price}")


bot = BreakOut()
print(bot.run())




