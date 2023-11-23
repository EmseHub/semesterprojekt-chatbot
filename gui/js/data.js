import courses from '/data/data-courses.json' assert { type: 'json' };
import students from '/data/data-students.json' assert { type: 'json' };


export const arrCourses = courses;
export const arrStudents = students.map(objStudent => ({ ...objStudent, letztesUpdate: new Date(objStudent.letztesUpdate) }));