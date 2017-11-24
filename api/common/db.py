from peewee import SqliteDatabase, Model

db = SqliteDatabase('cs6460.sqlite3')


def setup():
    from api.resources.stats import Stats
    from api.resources.user import User
    from api.resources.course import Course
    from api.resources.scrape import Scrape, Login
    db.connect()
    tables = [User, Stats, Course, Scrape, Login]
    db.drop_tables(tables, safe=True)
    db.create_tables(tables, safe=True)


class BaseModel(Model):
    class Meta:
        database = db
