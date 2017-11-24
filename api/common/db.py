from peewee import SqliteDatabase, Model

db = SqliteDatabase('cs6460.sqlite3')


def setup(clean=False):
    from api.resources.stats import Stats
    from api.resources.user import User
    from api.resources.course import Course
    from api.resources.scrape import Scrape, Login
    db.connect()
    tables = [User, Stats, Course, Scrape, Login]
    if clean:
        db.drop_tables(tables, safe=True)
    db.create_tables(tables, safe=True)

def teardown():
    db.close()

class BaseModel(Model):
    class Meta:
        database = db
