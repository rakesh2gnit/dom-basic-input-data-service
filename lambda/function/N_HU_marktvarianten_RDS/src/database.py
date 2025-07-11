from psycopg2 import pool
from constants import Constants
from custom_exception import DatabaseException
from utils import get_secret_dict

class Database:
    _instance = None
    _connection_pool = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._connection_pool:
            secret_name = Constants.DB_SECRET_NAME
            creds = get_secret_dict(secret_name)['SecretString']
            
            db_params = {
                "dbname": Constants.DB_NAME,
                "user": Constants.USERNAME,
                "password": creds,
                "host": Constants.HOST,
                "port": Constants.PORT
            }
            self._connection_pool = pool.SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                **db_params
            )

    def get_connection(self):
        try:
            connection = self._connection_pool.getconn()
            return connection
        except Exception as e:
            raise DatabaseException(f"Error getting connection from pool: {e}")
        
    def release_connection(self, connection):
        if connection:
            self._connection_pool.putconn(connection)
        
    def close_all_connections(self):
        if self._connection_pool:
            self._connection_pool.closeall()