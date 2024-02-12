from rule_engine.helpers import parse_json_file


def get_students():
    return parse_json_file("data/data-students.json")


def get_courses():
    return parse_json_file("data/data-courses.json")


def set_students(students):
    pass


def set_courses(courses):
    pass


# Zu Testzwecken nur zur Laufzeit gespeichert
students = get_students()
courses = get_courses()
