import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 
from sklearn.linear_model import Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.compose import TransformedTargetRegressor
class MyModel():
    def __init__(self):
        self.X = None #검증 셋 x
        self.y = None #검증 셋 y
        self.model = None

    def create_train_data(self, df):
        X = df.drop(['Price'],axis=1).iloc[:-1, ::]
        y = df['Price'].iloc[1:] #비트코인의 봉 평균가.
        train_X, test_X, train_y, test_y = train_test_split(X, y, test_size=0.3, random_state=24)
        self.X = test_X
        self.y = test_y
        return train_X, test_X, train_y, test_y

    def get_best_alpha(self, train_X, test_X, train_y, test_y): #알파를 튜닝
        best_alpha = 1
        best_mse = float('inf')
        for i in [1000,300,100,30,10,1]:
            self.model.set_params(regressor__regulator__alpha=i)
            self.model.fit(train_X, train_y) #바꾼 알파로 다시 피팅해본다.
            pred = self.model.predict(test_X)
            mse = ((test_y - pred) ** 2).mean()
            if best_mse > mse:
                best_mse = mse
                best_alpha = i
            print(f'mse: {mse}, alpha: {i}')
        return best_alpha

    def create_model(self, model_class):
        pipeline = Pipeline([
            ("std_scaler", StandardScaler()),
            ("poly_features",PolynomialFeatures(degree=3, include_bias=True)),
            ('regulator', model_class) #테스트할 모델만 변경해가며 성능을 측정한다.
        ])
        self.model = TransformedTargetRegressor(regressor=pipeline,transformer=StandardScaler()) #클래스 모델 변경
        train_X, test_X, train_y, test_y = self.create_train_data(X)
        alpha = self.get_best_alpha(train_X, test_X, train_y, test_y)
        self.model.set_params(regressor__regulator__alpha=alpha)
        self.model.fit(train_X, train_y) #최종 모델 피팅
        return 
    
    def visualize_plot(self, name): #시계열에 따른 예측도 시각화
        target = self.y
        pred = pd.Series(self.model.predict(self.X), index=target.index)
        plt.figure(figsize=(12,10))
        pred.sort_index().plot(label='model')
        target.sort_index().plot(label='target')
        plt.suptitle(f'{name}',fontsize=20)
        mse = ((target - pred) ** 2).mean()
        plt.title(f'MSE is {mse:.1f}')
        plt.legend()
