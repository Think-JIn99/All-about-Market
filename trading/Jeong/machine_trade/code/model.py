import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import Ridge, Lasso
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures, MinMaxScaler
from sklearn.model_selection import train_test_split
import joblib
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import TimeSeriesSplit
class MyModel():
    class DataConstructor():
        def remove_outliers(self, df):
            q_1 = df.apply(lambda x: np.quantile(x, 0.25))
            q_3 = df.apply(lambda x: np.quantile(x, 0.75))
            iqr = q_3 - q_1
            min_p = q_1 - 1.5 * iqr
            max_p = q_3 + 1.5 * iqr
            outliers = np.where((df < min_p) | (df > max_p))
            row, _ = outliers
            df = df.drop(df.index[row])
            return df

        def create_train_data(self, df, target='Price', outlier=True):
            if 'time' in df.columns:
                df.set_index('time',inplace=True)
            if not outlier:
                start_size = len(df)
                df = self.remove_outliers(df)
                end_size = len(df)
                print(f"outlier removed {start_size -  end_size}")
            X = df.drop([target], axis=1).iloc[:-1, ::] #다음날을 예측 해야한다
            y = df[target].iloc[1:] #비트코인의 봉 평균가.
            return train_test_split(X, y, test_size=0.3, random_state=24)

    def get_gridcv(self, model, param_grid, score = "neg_mean_squared_error"):
        time_cv = TimeSeriesSplit(n_splits=10)
        grid_model = GridSearchCV(estimator=model, scoring=score, param_grid=param_grid,
                                cv=time_cv, n_jobs=-1, verbose=3)
        return grid_model

    def create_ridge(self, X, y):
        ridge_model = Pipeline([
            ("max_scaler", MinMaxScaler()),
            ("poly_features",PolynomialFeatures(degree=3, include_bias=True)),
            ('estimator', Ridge(fit_intercept=True, random_state=42)) #테스트할 모델만 변경해가며 성능을 측정한다.
        ])
        param_grid = [
            {'estimator__alpha':[0.1,1,10,100,300,1000],
            'estimator__solver':["svd", "cholesky", "lsqr", "sparse_cg", "sag", "saga", "lbfgs"]
            }
        ]
        grid_model = self.get_gridcv(ridge_model, param_grid)
        grid_model.fit(X, y) #최종 모델 피팅
        return grid_model.best_estimator_
    
    def create_lasso(self, X, y):
        lasso_model = Pipeline([
            ("max_scaler", MinMaxScaler()),
            ("poly_features",PolynomialFeatures(degree=3, include_bias=True)),
            ('estimator', Lasso(fit_intercept=True, random_state=42)) #테스트할 모델만 변경해가며 성능을 측정한다.
        ])
        param_grid = [
            {'estimator__max_iter':[1000, 2000, 3000, 4000],
            'estimator__tol':[0.0001, 0.001, 0.01, 0.1],
            'estimator__alpha':[0.1,1,10,100,300,1000]
            }
        ]
        grid_model = self.get_gridcv(lasso_model, param_grid)
        grid_model.fit(X, y) #최종 모델 피팅
        return grid_model.best_estimator_
    
    def create_random_forest(self, X, y):
        rf_model = Pipeline([
        ('max_scaler', MinMaxScaler()),
        ('estimator',RandomForestClassifier(bootstrap=True, random_state=24, oob_score=True, max_features="sqrt"))
        ])
        param_grid = [
            {'estimator__max_depth':[100,200],
            'estimator__min_samples_leaf':[2,4,8,16],
            'estimator__min_samples_split':[2, 5, 10, 20]
            }
        ]
        grid_model = self.get_gridcv(rf_model, param_grid, score='roc_auc')
        grid_model.fit(X, y)
        return grid_model.best_estimator_

    def save_model(self, time_period):
        name = self.mode_class + str(time_period)
        path = "/Users/jin/Programming/Machine_Learning/All-about-Market/trading/Jeong/machine_trade/model/"
        file_name = f"{path}{name}.pkl"
        joblib.dump(self.model, file_name)
    
    def visualize_plot(self, X, y, name): #시계열에 따른 예측도 시각화
        target = y
        pred = pd.Series(X, index=target.index)
        plt.figure(figsize=(12,10))
        pred.sort_index().plot(label='model')
        target.sort_index().plot(label='target')
        plt.suptitle(f'{name}',fontsize=20)
        mse = ((target - pred) ** 2).mean()
        plt.title(f'MSE is {mse:.1f}')
        plt.legend()
    
