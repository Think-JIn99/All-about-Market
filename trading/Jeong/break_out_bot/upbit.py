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
        self.non_auth_headers = {"Accept": "application/json"}
    
    def create_payload(self, query_hash = None): #권한 토큰 생성을 위한 변수 생성
        payload = {'access_key': self.access_key,
                    'nonce': str(uuid.uuid4())}
        if query_hash:
            payload['query_hash'] = query_hash #payload에 쿼리 대입
            payload['query_hash_alg'] = "SHA512"
        return payload

    def get_headers(self, payload): #토큰 형태로 만들어 반환
        jwt_token = jwt.encode(payload, self.secret_key)
        authorize_token = 'Bearer {}'.format(jwt_token)
        headers = {"Authorization": authorize_token}
        return headers #jwt token을 돌려준다.

    def get_hash_query(self,query):
        if query:
            query_string = urlencode(query).encode() #url 인코딩
            m = hashlib.sha512() #해싱
            m.update(query_string)
            query_hash = m.hexdigest() #쿼리 해싱 값 대입
            return query_hash

    def create_request(self,method,url,headers,query=None):
        query_hash = self.get_hash_query(query) #쿼리의 해시 값 구함
        while True:
            try:
                if headers != self.non_auth_headers: #권한이 필요하지 않은 요청의 경우 바로 다시금 요청한다.
                    payload = self.create_payload(query_hash) #uuid를 초기화 해준다.
                    headers = self.get_headers(payload)
                res = requests.request(method, url, params = query, headers=headers)
                if (res.status_code == 200) or (res.status_code == 201):  #알맞은 응답이 오기까지 반복한다.
                    json = res.json() #결과를 json형태로 반환한다.
                    return json
                print(f"Retry to get api: {res.json()}")
            except Exception as e:
                print(e)

    def get_my_account(self): #계좌에 있는 자산 조회
        url = f"{self.server_url}accounts"
        response = self.create_request("GET", url, headers=None)
        return response

    def create_order(self, ticker, side, volume, price, ord_type): #매수,매도 주문을 생성한다.
        query = {
            'market':ticker, #종목명
            'side': side, #매수,매도
            'volume': volume, #매매량
            'price':price,#지정가격
            'ord_type': ord_type, #시장가, 지정가 타입 선택
        }
        url = f"{self.server_url}orders"
        res = self.create_request("POST", url, headers = None, query = query)
        return res
    
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

# b = Upbit()
# print(b.get_order_book("KRW-BTC"))
# print(b.get_current_price("KRW-BTC"))
# print(b.get_day_candle("KRW-BTC"))
# print(b.get_my_account())
# print(b.create_order('KRW-BTC','bid',100,10000,"limit"))

