import os
import pickle
import sklearn
import hashlib

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from typing import List
from fastapi import Depends,FastAPI
from sqlalchemy.orm import sessionmaker

from sqlalchemy.ext.declarative import declarative_base

from schema import PostGet
from datetime import datetime

from sqlalchemy import Column, Integer, String
from pydantic import BaseModel


# подключение к базе данных
SQLALCHEMY_DATABASE_URL = "postgresql://robot-startml-ro:pheiph0hahj1Vaif@postgres.lab.karpov.courses:6432/startml"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

app = FastAPI()

# загрузка модели
def get_model_path(path: str, model: str):
    if os.environ.get("IS_LMS") == "1":  # проверяем где выполняется код в лмс, или локально. Немного магии
        if model == 'model_test':
            MODEL_PATH = '/workdir/user_input/model_control'
        elif model == 'model_control':
            MODEL_PATH = '/workdir/user_input/model_control'
        else:
            raise ValueError('unknown model')
    else:
        MODEL_PATH = path

    return MODEL_PATH


def load_test_model():
    model_path = get_model_path('model_test.pkl', model = 'model_test')
    # LOAD MODEL HERE PLS :)

    loaded_model = pickle.load(open(model_path, 'rb'))

    return loaded_model
def load_control_model():
    model_path = get_model_path('model_control.pkl', model = 'model_control')
    # LOAD MODEL HERE PLS :)

    loaded_model = pickle.load(open(model_path, 'rb'))

    return loaded_model

model_control = load_control_model()
model_test = load_test_model()


# загрузка фич


def batch_load_sql(query: str) -> pd.DataFrame:
    CHUNKSIZE = 200000
    engine = create_engine(
        "postgresql://robot-startml-ro:pheiph0hahj1Vaif@"
        "postgres.lab.karpov.courses:6432/startml"
    )
    conn = engine.connect().execution_options(stream_results=True)
    chunks = []
    for chunk_dataframe in pd.read_sql(query, conn, chunksize=CHUNKSIZE):
        chunks.append(chunk_dataframe)
    conn.close()
    return pd.concat(chunks, ignore_index=True)

def load_features() -> pd.DataFrame:
    db = batch_load_sql('SELECT * FROM "v-susanin_features_lesson_22"')
    return db

df_users = load_features()

df_posts = batch_load_sql('SELECT * FROM "v-susanin_posts_features_lesson_22"')


posts = pd.read_sql(
    """SELECT * FROM public.post_text_df """,
    con="postgresql://robot-startml-ro:pheiph0hahj1Vaif@"
        "postgres.lab.karpov.courses:6432/startml"
)
posts.rename(columns = {'post_id':'id'}, inplace = True )


def posts_rec(id, time, limit):

    exp_group = get_exp_group(id, salt = salt, group_count = group_count)

    if exp_group == 'control':
        model = model_control
    elif exp_group == 'test':
        model = model_test
    else:
        raise ValueError('unknown group')

    # добавляем к фичам юзера список постов с их фичами
    user_test = df_users[df_users['user_id'] == id].iloc[0] # нужна именно серия
    
    df_test = df_posts.merge(pd.DataFrame(data=[user_test.values] * len(df_posts), columns=user_test.index),
                              left_index=True, right_index=True)
    
    # также добавляем время
    date_time = time
    
    df_dt = pd.DataFrame({'day':[date_time.day],
                      'hour': [date_time.hour]
                     }).iloc[0]
    
    df_test = df_test.merge(pd.DataFrame(data=[df_dt.values] * len(df_test), columns=df_dt.index),
                              left_index=True, right_index=True)

    # поменяем порядок колонок на тот, который был при обучении модели и проведём расчёт
    df_test['proba'] = model.predict_proba(df_test[['gender', 'age', 'country', 'city', 'exp_group', 'topic', 'TextCluster',
       'DistanceToCluster_0', 'DistanceToCluster_1', 'DistanceToCluster_2',
       'DistanceToCluster_3', 'DistanceToCluster_4', 'DistanceToCluster_5',
       'DistanceToCluster_6', 'DistanceToCluster_7', 'DistanceToCluster_8',
       'DistanceToCluster_9', 'DistanceToCluster_10', 'DistanceToCluster_11',
       'DistanceToCluster_12', 'DistanceToCluster_13', 'DistanceToCluster_14',
       'day', 'hour', 'os_iOS', 'source_organic']])[:, 1]

    t = df_test.sort_values('proba', ascending=False)

    posts_list = []

    for i in t['post_id']:
        if len(posts_list) < limit:
            posts_list.append(int(i))
            posts_list
        #print(posts_list)
    result = posts.loc[posts['id'].isin(posts_list)].to_dict('records')
    return {'exp_group': exp_group, 'recommendations': result}

def get_db():
    with SessionLocal() as db:
         return db

# определили класс для таблицы с постами
class Post(Base):
    __tablename__ = "post"
    id = Column(Integer, primary_key=True)
    text = Column(String)
    topic = Column(String)

salt = 'a_b_test'
group_count = 2
def get_exp_group(user_id: int,  salt, group_count) -> str:
    value_str = str(user_id) + salt
    value_num = int(hashlib.md5(value_str.encode()).hexdigest(), 16)
    if value_num % group_count == 1:
        exp_group = 'control'
    else:
        exp_group = 'test'
    return exp_group


class Response(BaseModel):
    exp_group: str
    recommendations: List[PostGet]

@app.get("/post/recommendations/", response_model=Response)
def recommended_posts(
		id: int,
		time: datetime = datetime.now(),
		limit: int = 10) -> Response:


    result = posts_rec(id = id, time = time, limit = limit)

    return result



