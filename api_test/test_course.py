from api.common import db
from api.resources import course
import unittest


class TestCourse(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        db.setup(clean=True)
        # See with a known course
        cls.course = course.Course(course_id='12345',
                                   course_name='new tech')
        cls.course.save()

    @classmethod
    def tearDownClass(cls):
        db.teardown()
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_non_existing_course(self):
        course_id = '77123'
        course_name = 'english 102'
        expected = course.Course(course_id=course_id,
                                 course_name=course_name)
        actual = course.create_if_not_exist(course_id, course_name)
        self.assertEqual(expected.course_name, actual.course_name)
        self.assertEqual(expected.course_id, actual.course_id)

    def test_create_non_existing_course_bad_args(self):
        course_id = 1234
        course_name = ['course', 'title']
        actual = course.create_if_not_exist(course_id, course_name)
        self.assertIsNone(actual)

    def test_get_existing_course_name(self):
        name = course.get_course_name(self.course.course_id)
        self.assertEqual(name, self.course.course_name)

    def test_get_non_existing_course_name(self):
        name = course.get_course_name('892341025701234')
        self.assertTrue(len(name) == 0)

    def test_get_course_name_bad_args(self):
        name = course.get_course_name(23487234)
        self.assertTrue(len(name) == 0)

    def test_duplicate_course(self):
        course.create_if_not_exist(self.course.course_id, self.course.course_name)
        self.assertEqual(course.Course
                         .select()
                         .where(course.Course.course_id == self.course.course_id)
                         .count(), 1)
