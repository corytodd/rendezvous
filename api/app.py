from flask import Flask, jsonify, request, abort
from functools import wraps
import werkzeug.exceptions as ex

from api.common import db, custom_abort
from api.resources import user
from api.resources import course
from api.resources import stats
from api.resources import scrape

app = Flask(__name__)
ver = "/api/v1.0"
custom_abort.register(ex.default_exceptions)

"""
There are some violations of the single-purpose principal in this app. The reason
this was done was because the Chrome extension needed simplification so the enroll/auth
and get stats/add enlisted course functions serve double duty. However, there are no 
double-side effects so we're not 100% in violation, rather just showing bad form.
CAT
"""

def check_authorization(func):

    @wraps(func)
    def check_api_key(*args, **kwargs):
        lts_id = request.args.get('lts_id')
        secret = request.args.get('secret')
        if not user.is_valid_user(lts_id, secret):
            abort(401)
        return func(*args, **kwargs)

    return check_api_key


@app.route(ver + '/enroll', methods=['POST'])
def enroll_user():
    """Enrolls a user in this service or authenticates the user if they
    already exist.

    /enroll?lts_id=<student_id>&secret=<some_secret_generated_earlier>
    """
    lts_id = request.args.get('lts_id')
    secret = request.args.get('secret')
    new_user = user.create_if_not_exist(lts_id, secret=secret)
    if not new_user:
        abort(401)
    return jsonify({"keep_this": new_user.secret})


@app.route(ver + '/addcourse', methods=['POST'])
@check_authorization
def add_course():
    """Adds a new course to this database

    /addcourse?lts_id=<student_id>&secret=<some_secret_generated_earlier>&course_id=<some_course_id>&course_name=<some_friendly_name>
    """
    course_id = request.args.get('course_id')
    course_name = request.args.get('course_name')
    new_course = course.create_if_not_exist(course_id, course_name)
    if not new_course:
        # Should never happen
        abort(500)
    return jsonify({"course_id": course_id, "course_name": course_name})


@app.route(ver + '/stats', methods=['GET'])
@check_authorization
def get_stats():
    """Get the stats for the specified user and add this course to users' list
    if not already listed

    /stats?lts_id=<student_id>&secret=<some_secret_generated_earlier>&course_id=<some_course_id>
    """
    lts_id = request.args.get('lts_id')
    course_id = request.args.get('course_id')
    user.add_course_to_user(lts_id, course_id)
    result = stats.get_stats(lts_id)
    if not result:
        abort(403)
    return jsonify(result)


@app.route(ver + '/tasks/scrape', methods=['POST'])
def task_scrape():
    """TODO Delete this debug method"""
    course_id = request.args.get('course_id')
    result = {}
    try:
        result = scrape.start_scrape(course_id)
    except scrape.NoLoginAvailable:
        abort(424)
    return jsonify(result)


@app.errorhandler(424)
def no_login_for_course(e):
    return 'No login credentials for course'


if __name__ == '__main__':
    debug = True
    db.setup(clean=debug)
    app.run(debug=debug)
