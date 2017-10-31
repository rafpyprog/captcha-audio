from io import BytesIO
import os
import sqlite3


class Database():
    def __init__(self, filename='captcha_data.db'):
        self.filename = filename
        self.conn = sqlite3.connect(self.filename)
        self.cursor = self.conn.cursor()
        self.table = 'captchas'

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()

    def initialize(self):
        create_table = (f'''CREATE TABLE {self.table} (image BLOB, '''
                       f'''audio BLOB, split INTEGER, solution TEXT);''')
        self.cursor.execute(create_table)
        self.commit()

    def insert_captcha(self, image, audio, split=99, solution=None):
        insert = f'''INSERT INTO {self.table} VALUES (?, ?, ?, ?);'''
        self.cursor.execute(insert, (image, audio, split, solution))
        self.commit()

    def get_captchas(self, split=None, solution=None):
        args = []
        select = f'''SELECT rowid, * FROM {self.table}'''

        if split is not None:
            args.append(int(split))
            select = select + ' WHERE split = ?'

        if solution is not None:
            if split:
                select = ' '.join([select, 'AND'])
            else:
                select = ' '.join([select, 'WHERE'])
            if solution is False:
                select = select + ' solution IS NULL'
            else:
                select = select + ' solution IS NOT NULL'

        select += ';'
        return self.cursor.execute(select, args)

    def get_captcha(self, rowid):
        select = f'''SELECT * FROM {self.table} WHERE rowid = ?;'''
        return self.cursor.execute(select, (rowid,))

    def delete_captcha(self, rowid):
        delete = f'''DELETE FROM {self.table} WHERE rowid = ?'''
        self.cursor.execute(delete, (rowid,))
        self.commit()

    def insert_solution(self, rowid, solution):
        if len(solution) != 6:
            raise ValueError(f'Tamanho inválido da solução {len(solution)}.')
        solution = solution.lower()
        update = f'''UPDATE {self.table} SET solution = ? WHERE rowid = ?;'''
        self.cursor.execute(update, (solution, rowid,))
        self.commit()
