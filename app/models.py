from . import db


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.BigInteger, primary_key=True)
    date = db.Column(db.DateTime, )
    country = db.Column(db.Text)
    text = db.Column(db.Text)

    def __repr__(self):
        return '<Post %d>' % self.id



