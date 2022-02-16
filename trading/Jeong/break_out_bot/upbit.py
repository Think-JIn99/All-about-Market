from os import access
import jwt
import uuid
import requests
import author
import hashlib
from urllib.parse import urlencode
class Upbit():
    def __init__(self):
        self.access_key = author.access_key
        self.secret_key = author.secret_key
        self.server_url = 'https://api.upbit.com/v1/'
        self.payload = {'access_key': self.access_key,
                    'nonce': str(uuid.uuid4())}
        self.non_auth_headers = {"Accept": "application/json"}

    def get_auth(self, payload):
        jwt_token = jwt.encode(payload, self.secret_key)
        authorize_token = 'Bearer {}'.format(jwt_token)
        headers = {"Authorization": authorize_token}
        return headers

    def get_my_account(self):
        headers = self.get_auth(self.payload)
        my_asset = requests.get(self.server_url + "accounts",headers=headers).json()
        return my_asset

    def get_current_price(self,ticker):
        url = f"{self.server_url}ticker?markets={ticker}"
        response = requests.get(url, headers=self.non_auth_headers)
        return response.json()
    
    def get_order_book(self, ticker):
        url = f"{self.server_url}orderbook?markets={ticker}"
        response = requests.request("GET", url, headers=self.non_auth_headers)
        return response.json()

    def create_payload(self, query_hash):
        payload = self.payload.copy()
        payload['query_hash'] = query_hash #payload에 쿼리 대입
        payload['query_hash_alg'] = 'SHA512'
        return payload

    def get_day_candle(self, ticker, candle_type, count): #candle_type -> min,day, period -> 1min, 3min, 1day..
        url = f"{self.server_url}candles/{candle_type}/?market={ticker}&count={count}"
        response = requests.get(url, headers=self.non_auth_headers).json()
        return response

    def get_hash_url(self, query):
        query_string = urlencode(query).encode() #url 인코딩
        m = hashlib.sha512() #해싱
        m.update(query_string)
        query_hash = m.hexdigest() #쿼리 해싱 값 대입
        return query_hash

    def make_order(self, ticker, volume, price,ord_type):
        query = {
            'market':ticker,
            'side':'bid',
            'volume': volume,
            'price':price,
            'ord_type': ord_type,
        }
        query_hash = self.get_hash_url(query)
        payload = self.create_payload(query_hash)
        headers = self.get_auth(payload)#헤더 반환
        res = requests.post(self.server_url + "orders",params=query,headers=headers).json()
        return res
    

