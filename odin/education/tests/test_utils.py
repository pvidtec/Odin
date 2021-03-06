from test_plus import TestCase

from django.conf import settings

from ..factories import (
    IncludedTaskFactory,
    SolutionFactory,
    CourseFactory,
    StudentFactory,
    WeekFactory,
    BaseUserFactory,
)

from ..models import Solution
from ..services import add_student
from ..utils import (
    get_passed_and_failed_tasks,
    get_solution_data,
    get_all_solved_student_solution_count_for_course,
)


class TestGetPassedAndFailedTasks(TestCase):
    def setUp(self):
        self.course = CourseFactory()
        self.week = WeekFactory(course=self.course)
        self.gradable_task = IncludedTaskFactory(course=self.course, week=self.week, gradable=True)
        self.non_gradable_task = IncludedTaskFactory(course=self.course, week=self.week, gradable=False)
        self.user = BaseUserFactory()
        self.student = StudentFactory()
        add_student(course=self.course, student=self.student)

    def test_returns_task_passed_when_there_is_passing_solution_for_it(self):
        passing_gradable_solution = SolutionFactory(user=self.user, task=self.gradable_task, status=Solution.OK)
        passing_non_gradable_solution = SolutionFactory(
            user=self.user, task=self.non_gradable_task, status=Solution.SUBMITTED_WITHOUT_GRADING
        )

        solution_data = {
            self.gradable_task: [passing_gradable_solution],
            self.non_gradable_task: [passing_non_gradable_solution]
        }
        result = get_passed_and_failed_tasks(solution_data)
        self.assertEqual(settings.TASK_PASSED, result.get(self.gradable_task.name))
        self.assertEqual(settings.TASK_PASSED, result.get(self.non_gradable_task.name))

    def test_returns_task_failed_when_there_are_only_failing_solutions_for_it(self):
        failing_solution = SolutionFactory(user=self.user, task=self.gradable_task, status=Solution.NOT_OK)
        solution_data = {
            self.gradable_task: [failing_solution]
        }
        result = get_passed_and_failed_tasks(solution_data)
        self.assertEqual(settings.TASK_FAILED, result.get(self.gradable_task.name))


class TestGetSolutionData(TestCase):
    def setUp(self):
        self.course = CourseFactory()
        self.week = WeekFactory(course=self.course)
        self.gradable_task = IncludedTaskFactory(course=self.course, week=self.week, gradable=True)
        self.non_gradable_task = IncludedTaskFactory(course=self.course, week=self.week, gradable=False)
        self.student = StudentFactory()
        self.user = BaseUserFactory()
        add_student(course=self.course, student=self.student)

    def test_solutions_to_tasks_are_added_successfully_to_solution_data(self):
        gradable_solution = SolutionFactory(user=self.user, task=self.gradable_task, status=Solution.OK)
        non_gradable_solution = SolutionFactory(
            user=self.user, task=self.non_gradable_task, status=Solution.SUBMITTED_WITHOUT_GRADING
        )

        solution_data, _ = get_solution_data(course=self.course, user=self.user)

        self.assertEqual([gradable_solution], solution_data.get(self.gradable_task))
        self.assertEqual([non_gradable_solution], solution_data.get(self.non_gradable_task))

    def test_task_is_not_added_as_key_if_no_solutions_for_it(self):
        solution_data, _ = get_solution_data(course=self.course, user=self.user)

        self.assertIsNone(solution_data.get(self.gradable_task))


class TestGetAllSolvedStudentSolutionCountForCourse(TestCase):
    def setUp(self):
        self.course = CourseFactory()
        self.week = WeekFactory(course=self.course)
        self.gradable_task = IncludedTaskFactory(course=self.course, week=self.week, gradable=True)
        self.non_gradable_task = IncludedTaskFactory(course=self.course, week=self.week, gradable=False)
        self.student = StudentFactory()
        self.user = BaseUserFactory()
        add_student(course=self.course, student=self.student)

    def test_correct_count_is_returned_when_student_has_passing_solutions(self):
        SolutionFactory(user=self.user, task=self.gradable_task, status=Solution.OK)
        SolutionFactory(
            user=self.user, task=self.non_gradable_task, status=Solution.SUBMITTED_WITHOUT_GRADING
        )

        students_passed_solution_count = get_all_solved_student_solution_count_for_course(course=self.course)

        self.assertEqual(2, students_passed_solution_count.get(self.user.email))

    def test_student_is_not_present_in_result_if_has_no_passing_solutions(self):
        SolutionFactory(user=self.user, task=self.gradable_task, status=Solution.NOT_OK)
        students_passed_solution_count = get_all_solved_student_solution_count_for_course(course=self.course)

        self.assertIsNone(students_passed_solution_count.get(self.user.email))

    def test_student_is_not_present_in_result_if_has_no_solutions(self):
        students_passed_solution_count = get_all_solved_student_solution_count_for_course(course=self.course)

        self.assertIsNone(students_passed_solution_count.get(self.user.email))
