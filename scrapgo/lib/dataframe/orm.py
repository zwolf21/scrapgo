import pandas as pd
import pymysql
from sqlalchemy import create_engine

from scrapgo.utils.fileutils import get_file_extension, read_json
from .dfutils import get_difference_from


QUERY_FORMAT = {
    'select': "SELECT {columns} FROM {table}",
    'select-where': "SELECT {columns} FROM {table} WHERE {where}",
    'max': "SELECT MAX({column}) FROM {table}",
    'max-where': "SELECT MAX({column}) FROM {table} WHERE {where}",
    'min': "SELECT MIN({column}) FROM {table}",
    'min-where': "SELECT MIN({column}) FROM {table} WHERE {where}",
    'count': "SELECT COUNT(*) FROM {table}",
    'count-where': "SELECT COUNT(*) FROM {table} WHERE {where}",
    'delete': "DELETE FROM {table}",
    'delete-where': "DELETE FROM {table} WHERE {where}",
}


class TableFrame(object):

    def __init__(self, table_name, path_connect_info_jsonfile=None, **conn_info):
        super().__init__(*args, **kwargs)
        if path_connect_info_jsonfile:
            if get_file_extension(path_connect_info_jsonfile) == '.json':
                conn_info = read_json(path_connect_info_jsonfile)
        self.con = self._get_db_connection(**conn_info)
        self.table = table_name

    def __del__(self):
        self.con.close()

    def _get_db_connection(self, **conn_info):
        db_backend = kwargs.get('backend', 'sqlite3')
        if db_backend == 'sqlite3':
            con = sqlite3.connect(**conn_info)
        elif db_backend == 'mysql':
            con_str_fmt = "mysql+pymysql://{user}:{passwd}@{host}:{port}/{db}?charset={charset}"
            con_str = con_str_fmt.format(**conn_info)
            engin = create_engine(con_str, encoding='utf-8')
            con = engin.connect()
        else:
            raise ValueError("DB backend only supported in sqlite3, mysql")
        return con

    def _get_now(self):
        return pd.Timestamp.now()

    def _get_query(self, kind, **kwargs, query_formats=QUERY_FORMAT):
        fmt = query_formats[kind]
        kwargs.setdefault('table', self.table_name)
        return fmt.format(**kwargs)

    def get_dataframe(self, query, **kwargs):
        dataframe = pd.read_sql(query, self.con, **kwargs)
        return dataframe

    def select(self, *columns, where=None, **kwargs):
        columns = ','.join(columns) or '*'
        if where is None:
            query = self._get_query('select', columns=columns, **kwargs)
        else:
            query = self._get_query(
                'select-where', columns=columns, where=where, **kwargs
            )
        df = self.get_dataframe(query)
        return df

    def max(self, column, where=None, **kwargs):
        if where is None:
            query = self._get_query('max', column=column, **kwargs)
        else:
            query = self._get_query(
                'max-where', column=column, where=where, **kwargs
            )
        df = self.get_dataframe(query)
        return df.loc[0, f"MAX({column})"]

    def min(self, column, where=None, **kwargs):
        if where is None:
            query = self._get_query('min', column=column, **kwargs)
        else:
            query = self._get_query(
                'min-where', column=column, where=where, **kwargs
            )
        df = self.get_dataframe(query)
        return df.loc[0, f"Min({column})"]

    def count(self, where=None, **kwargs):
        if where is None:
            query = self._get_query('count', **kwargs)
        else:
            query = self._get_query('count', where=where, **kwargs)
        df = self.get_dataframe(query)
        return df.loc[0, "COUNT(*)"]

    def insert_dataframe(self, dataframe, uniques, renames=None, updated=None, created=None, if_exists='append', **kwargs):
        if renames is not None:
            dataframe = dataframe.rename(columns=renames)

        table = self.select(uniques)
        if if_exists == 'append':
            dataframe = get_difference_from(dataframe, table, uniques)

        if updated is not None:
            dataframe[updated] = self._get_now()
        if created is not None:
            dataframe[created] = self._get_now()

        dataframe.to_sql(
            self.table_name, self.con,
            if_exists=if_exists,
            index=False
        )
