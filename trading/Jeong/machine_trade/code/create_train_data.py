import transform_feature
import author
import pandas as pd
def create_features():
    engine = author.raw_engine
    write_engine = author.processed_engine
    table_list = pd.read_sql("SHOW TABLES", con=engine).values.ravel() #DB에 있는 테이블 이름을 전부 가져옴
    for t in table_list:
        try:
            df = pd.read_sql("SELECT * FROM {}".format(t), con = engine)
            df.set_index(df.columns[0], inplace=True)
            df = df[~df.index.duplicated()] #중복 데이터를 제거해준다.
            print("Read data from sql completed!!")
        except Exception as e:
            print("Reading Failed")
            print(str(e))
        else:
            feature_tf = transform_feature.FeatureTransformer(df)
            is_coin = True  if "BTC" in t else False
            processed_df = feature_tf.transform(is_coin) #첫번째 데이터 프레임
            processed_df.index.name = "time"
            processed_df.to_sql(t, con = write_engine, if_exists='replace')
if __name__ == "__main__":
    create_features()