from mf import MF
from v4 import *
import sql
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




def make_recommendations(user_id, persona):
    if TRAIN_MODEL:
        data = get_training_data()
        # print(data)
        train_and_save(data,save_to='db')
    return_ids = get_user_data(user_id,persona,source='db')
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

def train_and_save(data,save_to='db'):
    start = time.time()
    print("> Training the NMF model over", data.shape, "items")
    mf = MF(data, K=20, alpha=0.001, beta=0.01, iterations=800)
    mf.train()
    saved_model = mf.full_matrix()
    end = time.time()
    print("> Elapsed Time to Train = ", end - start)
    if save_to == 'pickle':
        np.save('NMF', saved_model)
    if save_to == 'db':
        savetodb(saved_model)
    return 0


def get_user_data(user_id, persona, source='db'):
    if source == 'pickle':
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
            if len(return_ids) > TOP_N_ITEMS:
                break
        return return_ids
    if source == 'db':
        q13 = sql.q13
        q13 = q13 + str(user_id)
        if not INCLUDE_NON_PERSONA_ITEMS: q13 = q13 +" and pro.catagory='"+persona+"'"
        if not REPEAT_SKIPPED_ITEMS: q13 = q13 + " and pre.rating>"+str(CONSIDER_ITEM_IF_P_RATING_IS_ABOVE)+""
        if FAVOUR_NEW_ITEMS:q13 = q13 +" order by pre.rating desc,pre.product_id desc"
        q13 = q13+" limit "+str(TOP_N_ITEMS)+""
        result = sqlexecute(q13,())
        p_ids = [x.get('product_id') for x in result]
        return p_ids



def product_template(arr):
    if arr:
        print("_______________________________________________")
        print("| #id:", arr[0].get('id'))
        print("| Product Name:",arr[0].get('name'))
        print("| Type:", arr[0].get('catagory'))
        print("_______________________________________________")


def savetodb(a):
    start = time.time()
    sqlexecute(q11, ())
    sqlexecute(q10, ())
    for i in range(len(a)):
        for y in range(len(a[i])):
            product_id = i + 1
            user_id = y + 1
            rating = a[i][y]
            sqlexecute(q12, (product_id, user_id, rating))
    end = time.time()
    print("> Elapsed Time to Save to DB = ", end - start)
    return 0
