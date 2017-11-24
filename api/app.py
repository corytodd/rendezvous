from flask import Flask, jsonify, request, abort
from functools import wraps

from api.common import db
from api.resources import user
from api.resources import course
from api.resources import stats

app = Flask(__name__)

ver = "/api/v1.0"


def check_authorization(check_auth):
    @wraps(check_auth)
    def check_api_key(*args, **kwargs):
        lts_id = request.args.get('lts_id')
        secret = request.args.get('secret')
        if not user.is_valid_user(lts_id, secret):
            abort(401)


@app.route(ver + '/enroll', methods=['POST'])
def enroll_user():
    lts_id = request.args.get('lts_id')
    secret = request.args.get('secret')
    new_user = user.create_if_not_exist(lts_id, secret=secret)
    if not new_user:
        abort(401)
    return jsonify({"keep_this": new_user.secret})


@check_authorization
@app.route(ver + '/addcourse', methods=['POST'])
def add_course():
    course_id = request.args.get('course_id')
    course_name = request.args.get('course_name')
    new_course = course.create_if_not_exist(course_id, course_name)
    if not new_course:
        # Should never happen
        abort(500)
    return jsonify({"course_id": course_id, "course_name": course_name})


@check_authorization
@app.route(ver + '/stats', methods=['GET'])
def get_stats():
    lts_id = request.args.get('lts_id')
    course_id = request.args.get('course_id')
    user.add_course_to_user(lts_id, course_id)
    result = stats.get_stats(lts_id)
    if not result:
        abort(403)
    return jsonify(result)


@app.route(ver + '/tasks/scrape', methods=['POST'])
def task_scrape():
    return jsonify({})


if __name__ == '__main__':
    db.setup()
    app.run(debug=True)
