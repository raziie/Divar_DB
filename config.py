import dotenv
import os


dotenv.load_dotenv(override=True)
DEBUG = True
SECRET_KEY = os.getenv('SECRET_KEY')
