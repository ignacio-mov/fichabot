from flask_sqlalchemy import SQLAlchemy

from fichabot import app

db = SQLAlchemy()


class User(db.Model):

    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String(30))
    password = db.Column(db.String)

    def __repr__(self):
        return str(self.as_dict())

    def as_dict(self):
        password = ''.join('*' for _ in self.password)
        return {'user': {'id': self.id, 'name': self.name, 'password': password}}

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        with app.app_context():
            return User.query.all()

    @classmethod
    def get(cls, user_id):
        with app.app_context():
            return db.session.get(cls, user_id)

    def upsert(self):
        with app.app_context():
            user = User.get(self.id)
            if not user:
                db.session.add(self)
            else:
                user.name = self.name
                user.password = self.password
            db.session.commit()

    @staticmethod
    def delete(user_id):
        with app.app_context():
            User.get(user_id).query.delete()
            db.session.commit()
