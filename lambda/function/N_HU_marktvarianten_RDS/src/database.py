from psycopg2 import pool
from constants import Constants
import os
from custom_exception import DatabaseException
from utils import get_secret_dict

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
            creds = get_secret_dict(secret_name)['SecretString']
            db_params = {
                "dbname": os.environ.get("dbname"),
                "user": os.environ.get("username"),
                "password": creds,
                "host": os.environ.get("host"),
                "port": os.environ.get("port")  # Default 5432
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
            raise DatabaseException(f"Error getting connection from pool: {e}")
        
    def release_connection(self, conn):
        try:
            if conn:
                self._conn_pool.putconn(conn)
        except Exception as e:
            raise DatabaseException(f"Error releasing connection back to pool: {e}")
        
    def close_all_connections(self):
        try:
            if self._conn_pool:
                self._conn_pool.closeall()
        except Exception as e:
            raise DatabaseException(f"Error closing all connections in pool: {e}")