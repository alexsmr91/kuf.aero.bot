from sqlite3 import connect, Error


class Database:

    def __init__(self, filename='users.db'):
        try:
            self._conn = connect(filename)
            self._cursor = self._conn.cursor()
        except Error as err:
            print(err)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @property
    def connection(self):
        return self._conn

    @property
    def cursor(self):
        return self._cursor

    def commit(self):
        self.connection.commit()

    def close(self, commit=True):
        if commit:
            self.commit()
        self.connection.close()

    def execute(self, sql, params=None):
        self.cursor.execute(sql, params or ())

    def fetchall(self):
        return self.cursor.fetchall()

    def fetchone(self):
        return self.cursor.fetchone()

    def query(self, sql, params=None):
        self.cursor.execute(sql, params or ())
        return self.fetchall()


class UsersDataBase:

    def __init__(self, user_table='users'):
        self.user_table = user_table
        """
        CREATE TABLE users (user_id INTEGER, user_name TEXT, dep_mode INTEGER, arr_mode INTEGER);
        """

    def user_exists(self, user_id):
        res = None
        with Database() as db:
            try:
                res = db.query(f"SELECT * FROM `{self.user_table}` WHERE user_id = {user_id};")
            except Error as err:
                print(err)
        return bool(res)

    def add_user(self, user_id: str):
        with Database() as db:
            try:
                db.query(f"INSERT INTO `{self.user_table}` (`user_id`) VALUES ('{user_id}');")
            except Error as err:
                print(err)

    def edit_name(self, user_id: str, user_name: str):
        with Database() as db:
            try:
                db.query(f"UPDATE `{self.user_table}` SET `user_name`='{user_name}' WHERE  `user_id`={user_id};")
            except Error as err:
                print(err)

    def get_dep_mode(self, user_id: str):
        res = [[]]
        if self.user_exists(user_id):
            with Database() as db:
                try:
                    res = db.query(f"SELECT dep_mode FROM `{self.user_table}` WHERE  user_id = {user_id};")
                except Error as err:
                    print(err)
            return res[0][0]
        return -1

    def get_arr_mode(self, user_id: str):
        res = [[]]
        if self.user_exists(user_id):
            with Database() as db:
                try:
                    res = db.query(f"SELECT arr_mode FROM `{self.user_table}` WHERE  user_id = {user_id};")
                except Error as err:
                    print(err)
            return res[0][0]
        return -1

    def get_user_list(self):
        res = []
        with Database() as db:
            try:
                res = db.query(f"SELECT user_id FROM `{self.user_table}`;")

            except Error as err:
                print(err)
        rs = []
        for x in res:
            rs.append(x[0])
        return rs

    def get_user_names(self):
        res = []
        with Database() as db:
            try:
                res = db.query(f"SELECT user_name FROM `{self.user_table}`;")
            except Error as err:
                print(err)
        rs = []
        for x in res:
            rs.append(x[0])
        return rs

    def set_dep_mode(self, user_id: str, new_dep_mode: str):
        if self.user_exists(user_id):
            with Database() as db:
                try:
                    db.query(f"UPDATE `{self.user_table}` SET `dep_mode`='{new_dep_mode}' WHERE  `user_id`={user_id};")
                except Error as err:
                    print(err)

    def set_arr_mode(self, user_id: str, new_arr_mode: str):
        if self.user_exists(user_id):
            with Database() as db:
                try:
                    db.query(f"UPDATE `{self.user_table}` SET `arr_mode`='{new_arr_mode}' WHERE  `user_id`={user_id};")
                except Error as err:
                    print(err)

    def get_user_list_dep(self, dep_mode):
        res = []
        with Database() as db:
            try:
                res = db.query(f"SELECT user_id FROM `{self.user_table}` WHERE `dep_mode`={dep_mode};")
            except Error as err:
                print(err)
        rs = []
        for x in res:
            rs.append(x[0])
        return rs

    def get_user_list_arr(self, arr_mode):
        res = []
        with Database() as db:
            try:
                res = db.query(f"SELECT user_id FROM `{self.user_table}` WHERE `arr_mode`={arr_mode};")
            except Error as err:
                print(err)
        rs = []
        for x in res:
            rs.append(x[0])
        return rs
