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

    def edit_name(self, user_id: str, user_name: str):
        try:
            query = f"UPDATE `{databb}`.`{user_table}` SET `user_name`='{user_name}' WHERE  `user_id`={user_id};"
            self.connection.cursor().execute(query)
            self.connection.commit()
        except Error as err:
            print(err)

    def get_dep_mode(self, user_id: str):
        if self.user_exists(user_id):
            try:
                query = f"SELECT dep_mode FROM `{databb}`.`{user_table}` WHERE  user_id = {user_id};"
                curs = self.connection.cursor()
                curs.execute(query)
                res = curs.fetchall()
            except Error as err:
                print(err)
            return res[0][0]
        return -1

    def get_arr_mode(self, user_id: str):
        if self.user_exists(user_id):
            try:
                query = f"SELECT arr_mode FROM `{databb}`.`{user_table}` WHERE  user_id = {user_id};"
                curs = self.connection.cursor()
                curs.execute(query)
                res = curs.fetchall()
            except Error as err:
                print(err)
            return res[0][0]
        return -1

    def get_user_list(self):
        res = []
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

    def get_user_names(self):
        res = []
        try:
            query = f"SELECT user_name FROM `{databb}`.`{user_table}`;"
            curs = self.connection.cursor()
            curs.execute(query)
            res = curs.fetchall()
        except Error as err:
            print(err)
        rs = []
        for x in res:
            rs.append(x[0])
        return rs

    def set_dep_mode(self, user_id: str, new_dep_mode: str):
        if self.user_exists(user_id):
            try:
                query = f"UPDATE `{databb}`.`{user_table}` SET `dep_mode`='{new_dep_mode}' WHERE  `user_id`={user_id};"
                self.connection.cursor().execute(query)
                self.connection.commit()
            except Error as err:
                print(err)

    def set_arr_mode(self, user_id: str, new_arr_mode: str):
        if self.user_exists(user_id):
            try:
                query = f"UPDATE `{databb}`.`{user_table}` SET `arr_mode`='{new_arr_mode}' WHERE  `user_id`={user_id};"
                self.connection.cursor().execute(query)
                self.connection.commit()
            except Error as err:
                print(err)

    def get_user_list_dep(self, dep_mode):
        res = []
        try:
            query = f"SELECT user_id FROM `{databb}`.`{user_table}` WHERE `dep_mode`={dep_mode};"
            curs = self.connection.cursor()
            curs.execute(query)
            res = curs.fetchall()
        except Error as err:
            print(err)
        rs = []
        for x in res:
            rs.append(x[0])
        return rs

    def get_user_list_arr(self, arr_mode):
        res = []
        try:
            query = f"SELECT user_id FROM `{databb}`.`{user_table}` WHERE `arr_mode`={arr_mode};"
            curs = self.connection.cursor()
            curs.execute(query)
            res = curs.fetchall()
        except Error as err:
            print(err)
        rs = []
        for x in res:
            rs.append(x[0])
        return rs
