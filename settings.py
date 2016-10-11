from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

APP_SECRET_KEY = os.environ.get('APP_SECRET_KEY')
