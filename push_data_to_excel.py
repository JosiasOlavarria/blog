#!/usr/bin/env python3
import mysql.connector
from mysql.connector import Error, DatabaseError
import pandas as pd
conf_database = {'user': 'root', 'host': 'localhost', 'password': 'ace9029', 'database': 'blog', 'charset': 'utf8mb4', 'collation': 'utf8mb4_unicode_ci'}


class ToExcel():
    def __init__(self) -> None:
        self.conf = conf_database

    def pushAllData(self):
        try:
            with mysql.connector.connect(**self.conf) as connection:
                if connection.is_connected():
                    queryUsers = 'SELECT * FROM users'
                    df = pd.read_sql(queryUsers, connection)
                    df.to_excel('excel_tables/users.xlsx', index=False)
                else:
                    raise DatabaseError

            with mysql.connector.connect(**self.conf) as connection:
                if connection.is_connected():
                    queryPosts = 'SELECT * FROM posts'
                    df = pd.read_sql(queryPosts, connection)
                    df.to_excel('excel_tables/posts.xlsx', index=False)
                else:
                    raise DatabaseError
        except Error as err:
            print(f'\n> algo malo sucedio en la base de datos: {str(err)}')

    def updateRegisters(self):
        pass


if __name__ == '__main__':
    choice = input('\n> (1) para exportar tus datos a excel\n> (2) actualiza los registros en excel\n> Escribe: ')
    if choice == '1':
        export = ToExcel()
        export.pushAllData()
    elif choice == '2':
        update = ToExcel()
        update.updateRegisters()
