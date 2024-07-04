# import dotenv
import os


# dotenv.load_dotenv(override=True)


class Config:
    DEBUG = True
    # SECRET_KEY = os.getenv('SECRET_KEY')
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = os.getenv('SQL_PASS')
    MYSQL_HOST = '127.0.0.1'
    MYSQL_DATABASE = 'Divar'
    REDIS_PASSWORD = os.getenv('REDIS_PASS')
    # 'redis://localhost:6379/0'
