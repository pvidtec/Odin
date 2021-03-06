from django.db import models
from django.db.models import Q


class TaskQuerySet(models.QuerySet):

    def get_tasks_for(self, course):
        return self.filter(course=course)


class SolutionQuerySet(models.QuerySet):

    def get_solutions_for(self, user, task):
        return self.filter(student=user, task=task)

    def get_solved_solutions_for_student_and_course(self, user, course):
        q_expression = Q(task__gradable=True, status=2) | Q(task__gradable=False, status=6)

        filters = {'task__course': course, 'user': user}
        return self.filter(q_expression, **filters).order_by('task', '-id').distinct('task')
