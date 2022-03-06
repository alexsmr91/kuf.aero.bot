import os
from mysql.connector import connect, Error

my_sql_url = os.getenv('MY_SQL').split('#')
if not my_sql_url:
    exit("Error: no sql url provided")
userr, paass, hoost, poort, databb, user_table = my_sql_url


class Database:

    def __init__(self):
        try:
            self.connection = connect(host=hoost,
                                      user=userr,
                                      password=paass,
                                      port=poort,
                                      )
        except Error as err:
            print(err)

    def user_exists(self, user_id):
        try:
            query = f"SELECT * FROM `{databb}`.`{user_table}` WHERE user_id = {user_id};"
            curs = self.connection.cursor()
            curs.execute(query)
            res = curs.fetchone()
        except Error as err:
            print(err)
        return bool(res)

    def add_user(self, user_id: str):
        try:
            query = f"INSERT INTO `{databb}`.`{user_table}` (`user_id`) VALUES ('{user_id}');"
            self.connection.cursor().execute(query)
            self.connection.commit()
        except Error as err:
            print(err)

    def get_user_list(self):
        try:
            query = f"SELECT user_id FROM `{databb}`.`{user_table}`;"
            curs = self.connection.cursor()
            curs.execute(query)
            res = curs.fetchall()
        except Error as err:
            print(err)
        rs = []
        for x in res:
            rs.append(x[0])
        return rs
