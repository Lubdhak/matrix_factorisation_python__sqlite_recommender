import sqlite3
import pandas as pd
import numpy as np
from mf import MF
import time
db_con = sqlite3.connect('test.db')

def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def login(uname,persona):
    sql = "select id,username,persona from User where username='"+uname+"' and persona='"+persona+"'"
    cursor = db_con.execute(sql)
    for row in cursor:
        if row:
            print("Welcome ",uname)
            user_id = row[0]
            return user_id
    print("Invalid user")
    return False


def viewproduct(user_id,persona,rec_for_user_id):
    if rec_for_user_id:
        print(" 🤖 Recommends")
        id_str = list_to_string(rec_for_user_id)
        sql = "select * from Product where id in (" + id_str + ") limit 1"
    else:
        print("👀 Discover New")
        sql = "select * from Product where id not in (select product_id from Review where user_id=" + str(user_id) + ") limit 1"
    cursor = db_con.cursor()
    cursor.execute(sql)
    row = dictfetchall(cursor)
    if len(row) == 0:
        print("No more product to show")
        return False,rec_for_user_id
    print(row)
    id = row[0].get('id')
    if rec_for_user_id: rec_for_user_id.remove(id)
    return id,rec_for_user_id


def rateproduct(user_id,product_id,score):
    sql = "insert into Review (rating,user_id,product_id) values ("+ str(score) + ","+str(user_id)+"," + str(product_id)+") ON CONFLICT(user_id,product_id) DO UPDATE SET rating = "+ str(score) + ""
    cursor = db_con.cursor()
    cursor.execute(sql)
    db_con.commit()
    return 0


def list_to_string(mylist,lower=False):
    mystr = "'%s'" % "','".join(map(str, mylist))
    if lower: return mystr.lower()
    else: return mystr


def make_recommendations(user_id,persona,n_recommendations,train_model=False):
    if train_model:
        data = get_training_data()
        train_and_save(data)
    return_ids = get_user_data(user_id,persona,n_recommendations,THRESHOLD=3.0)
    return return_ids


def can_be_predicted(user_id,persona,shuffle_persona=False,repeat=False):
    if repeat:
        score = -1
    else:
        score = 0
    if shuffle_persona:
        sql = "select id as product_id from Product where id not in (select product_id from Review where user_id=" + str(
            user_id) + " and rating > " + str(score) + ")"
    else:
        sql = "select id as product_id from Product where catagory='"+persona+"' and id not in (select product_id from Review where user_id="+str(user_id)+" and rating > "+str(score)+")"
    cursor = db_con.cursor()
    cursor.execute(sql)
    rows = dictfetchall(cursor)
    x = [y.get('product_id') for y in rows]
    return x


def get_training_data():
    sql2 = "select product_id,user_id,rating as user_rating from Review"
    ratings = pd.read_sql_query(sql2, db_con)
    sql3 = "Select id from User"
    users = pd.read_sql_query(sql3, db_con)
    sql4 = "Select id from Product"
    items = pd.read_sql_query(sql4, db_con)
    n_users = users.id.unique().shape[0]
    n_items = items.id.unique().shape[0]
    data = np.zeros((n_users, n_items))
    for line in ratings.itertuples():
        data[line[2] - 1, line[1] - 1] = line[3]
    data = data.T  # 266 X 14
    return data


def train_and_save(data):
    start = time.time()
    # print("Training the NMF model over", data.shape, "items")
    mf = MF(data, K=20, alpha=0.001, beta=0.01, iterations=800)
    mf.train()
    saved_model = mf.full_matrix()
    np.save('NMF', saved_model)
    end = time.time()
    print("Elapsed Time to Train = ", end - start)
    return 0


def get_user_data(user_id,persona,n_recommendations,THRESHOLD=3.0):
    user_data_P = np.load('NMF.npy')[:, [user_id]]
    user_item_predicted = {}
    for i in range(len(user_data_P)):
        user_item_predicted[i + 1] = round(user_data_P[i][0])
    to_be_recomended = can_be_predicted(user_id, persona, shuffle_persona=False, repeat=False)
    return_ids = []
    for p in to_be_recomended:
        c = user_item_predicted.get(p, -1)
        if c > THRESHOLD:
            return_ids.append(p)
        if len(return_ids) > n_recommendations:
            break
    return return_ids