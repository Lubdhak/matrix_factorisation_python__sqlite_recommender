from mf import MF
from v4 import *
from sql import *
import numpy as np
import pandas as pd
import time

db_con = sqlite3.connect('test.db')

def login(uname, persona):
    row = sqlexecute(q1, (uname, persona))
    if row:
        print("Welcome ",uname)
        user_id = row[0].get('id',None)
        return user_id
    print("Invalid user")
    return False



def viewproduct(user_id, persona, rec_for_user_id):
    # print(rec_for_user_id)
    if rec_for_user_id:
        print("\n🤖 Recommends")
        idx = rec_for_user_id[0]
        row = sqlexecute(q2,(idx,))
        product_template(row)
        id = row[0].get('id')
        rec_for_user_id.remove(id)
        return id, rec_for_user_id

    else:
        print("\n👀 Discover New")
        row = sqlexecute(q3,(user_id,))
        if len(row) == 0:
            print("No more product to show")
            return False, rec_for_user_id
        id = row[0].get('id')
        product_template(row)
        return id, rec_for_user_id




def rateproduct(user_id, product_id, score):
    row = sqlexecute(q4,(score,user_id,product_id,score))
    return 0




def make_recommendations(user_id, persona, n_recommendations):
    if TRAIN_MODEL:
        data = get_training_data()
        # print(data)
        train_and_save(data)
    return_ids = get_user_data(user_id, persona, n_recommendations)
    return return_ids


def can_be_predicted(user_id, persona):
    if REPEAT_SKIPPED_ITEMS:
        score = -1
    else:
        score = 0
    if INCLUDE_NON_PERSONA_ITEMS:
        rows = sqlexecute(q8, (user_id, score))
    else:
        rows = sqlexecute(q9, (persona,user_id, score))
    x = [y.get('product_id') for y in rows]
    return x


def get_training_data():
    ratings = pd.read_sql_query(q5, db_con)
    users = pd.read_sql_query(q6, db_con)
    items = pd.read_sql_query(q7, db_con)
    n_users = users.id.unique().shape[0]
    n_items = items.id.unique().shape[0]
    data = np.zeros((n_users, n_items))
    for line in ratings.itertuples():
        data[line[2] - 1, line[1] - 1] = line[3]
    data = data.T  # 266 X 14
    return data


def get_movielens_data():
    mylist0flines = [line.rstrip() for line in open('u.csv')]
    data = np.zeros((943, 1682))
    for line in mylist0flines:
        x = line.split()
        user_id = int(x[0])
        movie_id = int(x[1])
        rating = int(x[2])
        data[user_id - 1, movie_id - 1] = rating
    data = data.T  # 266 X 14
    return data


def train_and_save(data):
    start = time.time()
    print("> Training the NMF model over", data.shape, "items")
    mf = MF(data, K=20, alpha=0.001, beta=0.01, iterations=800)
    mf.train()
    saved_model = mf.full_matrix()
    np.save('NMF', saved_model)
    end = time.time()
    print("> Elapsed Time to Train = ", end - start)
    return 0


def get_user_data(user_id, persona, n_recommendations):
    user_data_P = np.load('NMF.npy')[:, [user_id]]
    user_item_predicted = {}
    for i in range(len(user_data_P)):
        user_item_predicted[i + 1] = round(user_data_P[i][0])
    to_be_recomended = can_be_predicted(user_id, persona)
    return_ids = []
    for p in to_be_recomended:
        c = user_item_predicted.get(p, -1)
        if c > CONSIDER_ITEM_IF_P_RATING_IS_ABOVE:
            return_ids.append(p)
        if len(return_ids) > n_recommendations:
            break
    return return_ids


def product_template(arr):
    if arr:
        print("_______________________________________________")
        print("| #id:", arr[0].get('id'))
        print("| Product Name:",arr[0].get('name'))
        print("| Type:", arr[0].get('catagory'))
        print("_______________________________________________")