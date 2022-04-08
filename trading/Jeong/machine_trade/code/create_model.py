from model import MyModel
import model
import author
import pandas as pd
import numpy as np
from sklearn.linear_model import Ridge, Lasso
if __name__ == '__main__':
    engine = author.processed_engine
    table_list = pd.read_sql("SHOW TABLES", con=engine).values.ravel()
    model_class = [Lasso(alpha=10, fit_intercept=True, random_state=42), 
                    Ridge(alpha=10, solver="sparse_cg", random_state=42, fit_intercept=True)]
    
    for m in model_class:
        for t in table_list[:1]:
            try:
                df = pd.read_sql("SELECT * FROM {}".format(t), con = engine)
                df.set_index(df.columns[0], inplace=True)
                print("Read data from sql completed!!")
                model = MyModel()
                print(t)
                model.create_linear_model(m, df, outlier=True)
                model.save_model(t)
            except Exception as e:
                print(str(e))
    model = MyModel()
    model.create_random_forest(df,outlier=True)
    model.save_model('1d')
