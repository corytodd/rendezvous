import werkzeug.exceptions as ex


class NoPiazzaLoginForCourse(ex.HTTPException):
    def __init__(self):
        pass

    code = 424
    description = '<p>Beta server has no login credential for this course id</p>'


def register(exception_map):
    """Adds all custom exception to abort mapping"""
    exception_map[424] = NoPiazzaLoginForCourse
