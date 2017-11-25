import json
import uuid

import peewee
from peewee import CharField

from api.common.db import BaseModel, db
from api.common.util import validate_params


class User(BaseModel):
    lts_id = CharField(unique=True)
    secret = CharField()
    courses = peewee.BlobField(default=json.dumps([]))


def create_if_not_exist(lts_id, secret=None):
    """If the LTS id does not already exist, create the user and return their
    secret code. If the user does exist, then secret should be not None
    and match the value stored in the database

    Returns User object on success, otherwise None
    :param lts_id: online classroom student ID
    :type lts_id: str
    :param secret: ID associated with this user, if any
    :type secret: str
    :return User instance or None
    :rtype User:
    """
    secret = secret if secret else ''
    if not validate_params(str, lts_id, secret):
        return None
    try:
        with db.atomic():
            return User.create(lts_id=lts_id, secret=uuid.uuid4().hex)
    except peewee.IntegrityError:
        pass
    user = User.get(User.lts_id == lts_id)
    return user if user.secret == secret else None


def is_valid_user(lts_id, secret):
    """Returns true if user is valid, otherwise false

    :param lts_id: Student ID
    :type lts_id: str
    :param secret: Students auth secret
    :type secret: str
    :return True if valid user, else false
    :rtype bool:
    """
    try:
        user = User.get((User.lts_id == lts_id) & (User.secret == secret))
        return user is not None
    except peewee.DoesNotExist:
        return False


def add_course_to_user(lts_id, course_id):
    """Add this course id to the user's course list
    """
    try:
        user = User.get(User.lts_id == lts_id)
        prev = json.loads(user.courses)
        user.courses = json.dumps(list(set(prev + [course_id])))
        user.save()
        return True
    except peewee.DoesNotExist:
        return False
