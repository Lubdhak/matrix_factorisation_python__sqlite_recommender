import sqlite3

db_con = sqlite3.connect('test.db')


def sqlexecute(query, params):
    final_param = []
    for i in params:
        # print(i)
        if isinstance(i, list):
            temp = []
            for x in range(len(i)):
                temp.append(str(i[x]))
            final_param.append(lts(temp))
            continue
        final_param.append(i)
    final_param = tuple(final_param)
    # print("Query=>", query)
    # print("Final Params are:=", final_param)
    cursor = db_con.cursor()
    cursor.execute(query, final_param)
    result = dictfetchall(cursor)
    db_con.commit()
    cursor.close()
    return result


def dictfetchall(cursor):
    try:
        columns = [col[0] for col in cursor.description]
        return [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]
    except Exception as e:
        # print(e)
        return []


def lts(mylist, lower=False):
    mystr = "'%s'" % "','".join(map(str, mylist))
    if lower:
        return mystr.lower()
    else:
        return mystr


q1 = "select id,username,persona from User where username=? and persona=?;"

q2 = "select * from Product where id in (?) limit 1;"

q3 = "select * from Product where id not in (select product_id from Review where user_id=?) limit 1"

q4 = "insert into Review (rating,user_id,product_id) values (?,?,?) ON CONFLICT(user_id,product_id) DO UPDATE SET rating = ?"

q5 = "select product_id,user_id,rating as user_rating from Review"

q6 = "Select id from User"

q7 = "Select id from Product"

q8 = "select id as product_id from Product where id not in (select product_id from Review where user_id=? and rating > ?)"

q9 = "select id as product_id from Product where catagory=? and id not in (select product_id from Review where user_id=? and rating >?)"
