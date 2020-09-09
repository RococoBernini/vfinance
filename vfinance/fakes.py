from faker import Faker
from sqlalchemy.exc import IntegrityError
import random
from vfinance.extensions import db
from vfinance.models import User

fake = Faker()

def fake_user(count = 10):
    # register myself
    user = User(
        username = "ccjccy77828",
        cash = 10000000,
        position = 0
    )
    user.set_password("sulamoon")
    db.session.add(user)
    for i in range(count):
        simple_file = fake.simple_profile()
        user = User(
            username = simple_file["username"],
            cash = 1000000,
            position = 0
        )
        fake_password = fake.password(length = 12)
        user.set_password(fake_password)
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()     
    
   