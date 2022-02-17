from urllib import response
import jwt
import uuid
import requests
import author
import hashlib
from urllib.parse import urlencode
import time
class Upbit():
    def __init__(self):
        self.access_key = author.access_key
        self.secret_key = author.secret_key
        self.server_url = 'https://api.upbit.com/v1/'
        # self.payload = {'access_key': self.access_key,
        #             'nonce': str(uuid.uuid4())}
        self.non_auth_headers = {"Accept": "application/json"}

    def get_headers(self, payload):
        jwt_token = jwt.encode(payload, self.secret_key)
        authorize_token = 'Bearer {}'.format(jwt_token)
        headers = {"Authorization": authorize_token}
        return headers

    def create_request(self,method,url,headers,params = None):
        res = requests.request(method, url, params = params,headers=headers)
        # while (res.status_code != 200 and res.status_code != 201):
        #     res = requests.request(method, url, params = params, headers=headers)
        #     print(f"Retry to get api: {res.json()}")
        #     time.sleep(0.1)  
        json = res.json()
        return json

    def get_my_account(self):
        url = f"{self.server_url}accounts"
        response = self.create_request("GET", url, headers=self.get_headers(self.create_payload()))
        return response

    def get_current_price(self,ticker):
        url = f"{self.server_url}ticker?markets={ticker}"
        response = self.create_request("GET", url, headers=self.non_auth_headers)
        return response
    
    def get_order_book(self, ticker):
        url = f"{self.server_url}orderbook?markets={ticker}"
        response = self.create_request("GET", url, headers=self.non_auth_headers)
        return response

    def get_day_candle(self, ticker, candle_type="days", count = 1): #candle_type -> min,day, period -> 1min, 3min, 1day..
        url = f"{self.server_url}candles/{candle_type}/?market={ticker}&count={count}"
        response = self.create_request("GET",url, headers=self.non_auth_headers)
        return response

    def create_payload(self, query_hash = None):
        payload = {'access_key': self.access_key,
                    'nonce': str(uuid.uuid4())}
        if query_hash:
            payload['query_hash'] = query_hash #payload에 쿼리 대입
            payload['query_hash_alg'] = "SHA512"
        return payload

    def get_hash_url(self, query):
        query_string = urlencode(query).encode() #url 인코딩
        m = hashlib.sha512() #해싱
        m.update(query_string)
        query_hash = m.hexdigest() #쿼리 해싱 값 대입
        return query_hash

    def create_order(self, ticker, side, volume, price, ord_type):
        query = {
            'market':ticker,
            'side': side, #매수,매도
            'volume': volume,
            'price':price,
            'ord_type': ord_type, #시장가, 지정가
        }
        query_hash = self.get_hash_url(query)
        payload = self.create_payload(query_hash)
        headers = self.get_headers(payload)#헤더 반환
        url = f"{self.server_url}orders"
        res = self.create_request("POST",url,headers,query)
        return res
    
b = Upbit()
# print(b.get_order_book("KRW-BTC"))
# print(b.get_current_price("KRW-BTC"))
# print(b.get_day_candle("KRW-BTC"))
# print(b.get_my_account())
print(b.create_order('KRW-BTC','bid',100,10000,"limit"))

