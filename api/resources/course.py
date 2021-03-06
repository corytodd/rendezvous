import peewee
from peewee import CharField

from api.common.db import BaseModel
from api.common.util import validate_params


class Course(BaseModel):
    """Online course model maps course id to a name"""
    course_id = CharField(null=False)
    course_name = CharField(null=False)


def create_if_not_exist(course_id, course_name):
    """If the course_id id does not already, create the course and return the
    object. If the course does exist, nothing changes. This will always return
    a course instance if valid args are provided.

    :param course_id: online classroom ID
    :type course_id: str
    :param course_name: String name of the course
    :type course_name: str
    :return Course instance
    :rtype Course:
    """
    if not validate_params(str, course_id, course_name):
        return None
    course, _ = Course.get_or_create(course_id=course_id,
                                     course_name=course_name)
    return course


def get_course_name(course_id):
    """Returns the course name for the specified course_id.
    If the name is not found, an empty string is returned"""
    if validate_params(str, course_id):
        try:
            course = Course.get(Course.course_id == course_id)
            return course.course_name
        except peewee.DoesNotExist:
            pass
    return ''
