from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)
# app.app_context().push()
#
# db.create_all()

class ToDO(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Integer, default=0)
    date_created = db.Column(db.DateTime, default=datetime.utcnow())

    def __repr__(self):
        return '<Task %r>' % self.id


class RfidTable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rfid_number = db.Column(db.String(200), nullable=False)
    photo = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(200), nullable=True, default=0)

    def __repr__(self):
        return '<Task %r>' % self.id

@app.route('/')
def index():
    return "hello"


if __name__ == "__main__":
    app.run(debug=True)
