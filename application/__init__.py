from flask import Flask
from dotenv import load_dotenv


app = Flask(__name__)
load_dotenv()
app.debug=True
app.config.from_object('config.Config')
