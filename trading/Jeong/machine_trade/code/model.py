from platform import machine
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 
from sklearn.linear_model import Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures, MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.compose import TransformedTargetRegressor
import joblib
from joblib import dump #모델을 저장한다.

class MyModel():
    def __init__(self):
        self.X = None #검증 셋 x
        self.y = None #검증 셋 y
        self.model = None
        self.mode_class = None

    def create_train_data(self, df, target='Price', outlier=False):
        if not outlier:
            start_size = len(df)
            df = self.remove_outliers(df)
            end_size = len(df)
            print(f"outlier removed {start_size -  end_size}")
        X = df.drop([target], axis=1).iloc[:-1, ::] #다음날을 예측 해야한다
        y = df[target].iloc[1:] #비트코인의 봉 평균가.
        train_X, test_X, train_y, test_y = train_test_split(X, y, test_size=0.3, random_state=24)
        self.X = test_X
        self.y = test_y
        return train_X, test_X, train_y, test_y

    def get_best_alpha(self, train_X, test_X, train_y, test_y): #알파를 튜닝
        best_alpha = 1
        best_mse = float('inf')
        for i in [10000,3000,1000,300,100,30,10,1]:
            self.model.set_params(regressor__regulator__alpha=i)
            self.model.fit(train_X, train_y) #바꾼 알파로 다시 피팅해본다.
            pred = self.model.predict(test_X)
            mse = ((test_y - pred) ** 2).mean()
            if best_mse > mse:
                best_mse = mse
                best_alpha = i
            print(f'mse: {mse}, alpha: {i}')
        return best_alpha

    def create_linear_model(self, model_class, df, target='Price', outlier=False):
        pipeline = Pipeline([
            ("max_scaler", MinMaxScaler()),
            ("poly_features",PolynomialFeatures(degree=3, include_bias=True)),
            ('regulator', model_class) #테스트할 모델만 변경해가며 성능을 측정한다.
        ])
        #타겟 값 또한 정규화를 진행하기 위해 사용 
        # self.model = TransformedTargetRegressor(regressor=pipeline, transformer=StandardScaler()) #클래스 모델 변경
        self.mode_class = type(model_class).__name__
        train_X, test_X, train_y, test_y = self.create_train_data(df, outlier=outlier, target=target) #모델을 생성할 데이터 셋이 필요하다
        alpha = self.get_best_alpha(train_X, test_X, train_y, test_y)
        self.model.set_params(regressor__regulator__alpha=alpha)
        self.model.fit(train_X, train_y) #최종 모델 피팅
        return
    
    def create_random_forest(self, df, target='Price', outlier=False,start=2,end=100,gap=5):
        rf_model = Pipeline([
        ('max_scaler', MinMaxScaler()),
        ('machine',RandomForestRegressor(bootstrap=True, random_state=24, oob_score=True, max_features='sqrt'))
        ])
        self.mode_class = "RandomForest"
        train_X, test_X, train_y, test_y = self.create_train_data(df, outlier=outlier, target=target) #모델을 생성할
        def tune_param(param):
            # best_param = 2
            # best_mse = float('inf')
            # for i in range(start,end,gap):
            #     if param == "depth":
            #         rf_model.set_params(machine__max_depth=i)
            #     elif param == "split":
            #         rf_model.set_params(machine__min_samples_split=i)
            #     elif param == "max_leaf":
            #         rf_model.set_params(machine__max_leaf_nodes=i)
            #     elif param =="min_leaf":
            #         rf_model.set_params(machine__min_samples_leaf=i)
            #     rf_model.fit(train_X, train_y)
            #     rf_pred = rf_model.predict(test_X)
            #     mse = ((test_y - rf_pred) ** 2).mean()
            #     if best_mse > mse:
            #         best_mse = mse
            #         best_param = i
            #     print(f'param: {param} mse: {mse}, alpha: {i}')
            # return best_param

        best_depth = tune_param("depth")
        best_split = tune_param("split")
        best_min_leaf = tune_param("min_leaf")
        new_rf = RandomForestRegressor(bootstrap=True, random_state=24, max_depth=2000,
        min_samples_split = best_split, min_samples_leaf=best_min_leaf)
        rf_model.set_params(machine=new_rf)
        self.model = rf_model
        self.model.fit(train_X, train_y)


    def remove_outliers(self, df):
        q_1 = df.apply(lambda x: np.quantile(x, 0.25))
        q_3 = df.apply(lambda x: np.quantile(x, 0.75))
        iqr = q_3 - q_1
        min_p = q_1 - 2.0 * iqr
        max_p = q_3 + 2.0 * iqr
        outliers = np.where((df < min_p) | (df > max_p))
        row, _ = outliers
        df = df.drop(df.index[row])
        return df

    def save_model(self, time_period):
        name = self.mode_class + str(time_period)
        path = "/Users/jin/Programming/Machine_Learning/All-about-Market/trading/Jeong/machine_trade/model/"
        file_name = f"{path}{name}.pkl"
        joblib.dump(self.model, file_name)
    
