from flask_login import UserMixin
from cs50 import SQL

class User(UserMixin):
    def __init__(self, id_, name, email, profile_pic):
        self.id = id_
        self.name = name
        self.email = email
        self.profile_pic = profile_pic

    @staticmethod
    def get(user_id):
        db = SQL("sqlite:///goals.db")
        user = db.execute(
            "SELECT * FROM user WHERE id = :id", id=user_id)
        if not user:
            return None
        user = user[0]
        user = User(
            id_=user['id'], name=user['name'], email=user['email'], profile_pic=user['profile_pic']
        )
        return user

    @staticmethod
    def create(id_, name, email, profile_pic):
        db = SQL("sqlite:///goals.db")
        db.execute(
            "INSERT INTO user (id, name, email, profile_pic) "
            "VALUES (?, ?, ?, ?)",
            (id_, name, email, profile_pic),
        )