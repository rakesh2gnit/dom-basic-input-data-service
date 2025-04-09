from psycopg2 import pool
from constants import Constants
import os
import utils

class Database:
    _instance = None
    _conn_pool = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._conn_pool:
            secret_name = Constants.DB_SECRET_NAME
            creds = utils.get_secret_dict(secret_name)['SecretString']
            db_params = {
                "dbname": os.getenv("dbname"),
                "user": os.getenv("username"),
                "password": creds,
                "host": os.getenv("host"),
                "port": os.getenv("port")
            }
            self._conn_pool = pool.SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                **db_params
            )

    def get_connection(self):
        try:
            conn = self._conn_pool.getconn()
            if conn:
                return conn
        except Exception as e:
            raise utils.GenericException(f"Error getting connection from pool: {e}") from e
        
    def release_connection(self, conn):
        try:
            if conn:
                self._conn_pool.putconn(conn)
        except Exception as e:
            raise utils.GenericException(f"Error releasing connection back to pool: {e}") from e
        
    def close_all_connections(self):
        try:
            if self._conn_pool:
                self._conn_pool.closeall()
        except Exception as e:
            raise utils.GenericException(f"Error closing all connections in pool: {e}") from e