from flask import Flask, render_template
from sqlalchemy.orm import sessionmaker
from repository import app as routes_app
from connections import engine
from models import User, BankAccount


Base.metadata.create_all(bind=engine)

app = Flask(__name__)
app.register_blueprint(routes_app)

if __name__ == '__main__':
    app.run(debug=True, port=5432)