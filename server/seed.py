#seed.py

from app import db
from models import User

# Create a few users
def seed_users() :
    db.session.add(User(username='user1', email='user1@example.com'))
    db.session.add(User(username='user2', email='user2@example.com'))
    db.session.commit()
    print('Users seeded')

