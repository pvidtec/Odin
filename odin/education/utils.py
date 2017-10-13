from .models import Solution


def get_passed_and_failed_tasks(solution_data):
    passed_or_failed = {}
    for task, solutions in solution_data.items():
        if task.gradable:
            for solution in solutions:
                if solution.status == Solution.OK:
                    passed_or_failed[task.name] = "Passed"
            if not passed_or_failed.get(task.name):
                passed_or_failed[task.name] = "Failed"
        else:
            for solution in solutions:
                if solution.status == Solution.SUBMITTED_WITHOUT_GRADING:
                    passed_or_failed[task.name] = "Passed"
            if not passed_or_failed[task.name]:
                passed_or_failed[task.name] = "Failed"

    return passed_or_failed


def get_solution_data(course, student):
    all_solutions = student.solutions.filter(task__topic__course=course).prefetch_related('task')
    solution_data = {}
    for solution in all_solutions:
        task_solutions = solution_data.get(solution.task)
        if task_solutions:
            solution_data[solution.task] += solution
        else:
            solution_data[solution.task] = [solution]

    passed_and_failed = get_passed_and_failed_tasks(solution_data)

    return solution_data, passed_and_failed
