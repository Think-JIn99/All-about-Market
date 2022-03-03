import joblib
import author
import pandas as pd
import numpy as np
from sklearn.linear_model import Ridge,Lasso
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from joblib import dump #모델을 저장한다.

def remove_outliers(df):
    q_1 = df.apply(lambda x: np.quantile(x,0.25))
    q_3 = df.apply(lambda x: np.quantile(x,0.75))
    iqr = q_3 - q_1
    min_p = q_1 - 2.0 * iqr
    max_p = q_3 + 2.0 * iqr
    outliers = np.where((df < min_p) | (df > max_p))
    row, _ = outliers
    df = df.drop(df.index[row])
    return df

def create_model():
    ridge = Pipeline([
    ("poly_features",PolynomialFeatures(degree=3, include_bias=True)),
    ('std_scaler', StandardScaler()),
    ('regulator', Ridge(alpha=10,solver="cholesky",random_state=42))
    ])
    lasso = Pipeline([
        ("poly_features",PolynomialFeatures(degree=3, include_bias=True)),
        ('std_scaler', StandardScaler()),
        ('regulator', Lasso(alpha=10,random_state=42,fit_intercept=True))
    ])
    rf_model = Pipeline([
        ('std_scaler', StandardScaler()),
        ('machine',RandomForestRegressor(bootstrap=True, random_state=42, oob_score=True))
    ])
    return ridge, lasso, rf_model

def create_train_data(df):
    X = df.drop(['Adj Close'],axis=1)
    y = df['Adj Close'] #비트코인의 봉 평균가.
    train_X, test_X, train_y, test_y = train_test_split(X, y, test_size=0.3, random_state=24)
    return train_X, test_X, train_y, test_y

def find_best_alpha(train_X, train_y, test_X, test_y, model):
    best_alpha = 1
    best_mse = float('inf')
    for i in [1000,300,100,30,10,1]:
        model.set_params(regulator__alpha=i)
        model.fit(train_X, train_y)
        pred = model.predict(test_X)
        mse = ((test_y - pred) ** 2).mean()
        if best_mse > mse:
            best_mse = mse
            best_alpha = i
        print(f'mse: {mse}, alpha: {i}')
    return best_alpha

if __name__ == '__main__':
    engine = author.processed_engine
    ridge, lasso, rf = create_model()
    timespan = ['2m','5m','15m','1h','1d']
    for t in timespan:
        df = pd.read_sql("SELECT * FROM BTCUSD_{}".format(t), engine)
        df.set_index('time',inplace=True)
        df = remove_outliers(df) if t == '1d' else df

        train_X, test_X, train_y, test_y = create_train_data(df)

        r_alpha = find_best_alpha(train_X, train_y, test_X, test_y, ridge)
        ridge.set_params(regulator__alpha=r_alpha)
        ridge.fit(train_X, train_y)

        l_alpha = find_best_alpha(train_X, train_y, test_X, test_y, lasso)
        lasso.set_params(regulator__alpha=l_alpha)
        lasso.fit(train_X, train_y)

        rf.fit(train_X, train_y)

        for name, model in zip(["Ridge","Lasso","RandFore"],[ridge,lasso,rf]):
            file_name = f"{name}_{t}.pkl"
            joblib.dump(model, file_name)
