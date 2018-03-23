from rest_framework import status
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, get_object_or_404
from rest_framework.response import Response

from odin.apis.mixins import ServiceExceptionHandlerMixin

from odin.education.models import (
    Course,
    Student,
    Teacher,
    IncludedTask,
    IncludedTask,
    Week,
    ProgrammingLanguage,
    # make relation for course and programing language
)

from odin.education.services import (
    get_gradable_tasks_for_course,
    create_included_task,
    create_test_for_task,
)

from odin.education.apis.permissions import (
    StudentCourseAuthenticationMixin,
    IsUserStudentOrTeacherMixin,
    IsStudentOrTeacherInCourseMixin,
    TeacherCourseAuthenticationMixin,
)


class StudentCoursesApi(IsUserStudentOrTeacherMixin, ListAPIView):
    class Serializer(serializers.ModelSerializer):
        students_count = serializers.SerializerMethodField()
        description = serializers.CharField(source='description.verbose')

        class Meta:
            model = Course
            fields = ('id',
                      'name',
                      'start_date',
                      'end_date',
                      'logo',
                      'slug_url',
                      'description',
                      'students_count')

        def get_students_count(self, obj):
            return obj.students.filter(is_active=True).count()

    serializer_class = Serializer

    def get_queryset(self):
        user = self.request.user

        student = user.downcast(Student)
        teacher = user.downcast(Teacher)

        if teacher:
            return Course.objects\
                .filter(teachers__in=[teacher])\
                .order_by('-id')

        return Course.objects\
                     .filter(course_assignments__student=student)\
                     .order_by('-id')


class CourseDetailApi(StudentCourseAuthenticationMixin, APIView):
    class CourseSerializer(serializers.ModelSerializer):

        problems = serializers.SerializerMethodField()

        class Meta:
            model = Course
            fields = ('id',
                      'name',
                      'start_date',
                      'end_date',
                      'logo',
                      'slug_url',
                      'problems')

        def get_problems(self, obj):
            return [
                {
                    'id': task.id,
                    'name': task.name,
                    'gradable': task.gradable,
                    'week': task.week.number,
                    'description': task.description,
                    'last_solution': task.last_solution and {
                        'id': task.last_solution.id,
                        'status': task.last_solution.verbose_status,
                        'code': task.last_solution.code
                    } or None
                } for task in obj.tasks
            ]

    def get_queryset(self):
        return Course.objects.prefetch_related('weeks__included_tasks')

    def get(self, request, course_id):
        course = get_object_or_404(self.get_queryset(), pk=course_id)
        student = self.request.user.downcast(Student)

        course.tasks = get_gradable_tasks_for_course(course=course, student=student)

        return Response(self.CourseSerializer(instance=course).data)


class TeacherCourseDetailApi(TeacherCourseAuthenticationMixin, APIView):
    class Serializer(serializers.ModelSerializer):

        weeks = serializers.SerializerMethodField()

        class Meta:
            model = Course
            fields = (
                'id',
                'name',
                'start_date',
                'end_date',
                'logo',
                'slug_url',
                'weeks',
            )

        def get_weeks(self, obj):
            return [
                {
                    'id': week.id,
                    'number': week.number,
                    'tasks': [
                        {
                            'id': task.id,
                            'name': task.name,
                            'gradable': task.gradable,
                            'description': task.description,
                        } for task in week.included_tasks.all()
                    ]
                } for week in obj.weeks.all()
            ]

    def get(self, request, course_id):
        course = get_object_or_404(Course, pk=course_id)

        return Response(self.Serializer(instance=course).data)


class CreateTaskApi(ServiceExceptionHandlerMixin, APIView):
    class Serializer(serializers.Serializer):
        course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())
        name = serializers.CharField()
        code = serializers.CharField()
        description = serializers.CharField()
        gradable = serializers.BooleanField()
        week = serializers.PrimaryKeyRelatedField(queryset=Week.objects.all())

    def post(self, request, course_id):
        init_data = request.data
        init_data['course'] = course_id
        serializer = self.Serializer(data=init_data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        code = data.pop('code')

        included_task = create_included_task(**data)
        included_task.save()
        included_test = create_test_for_task(
            task=included_task,
            code=code,
            language=ProgrammingLanguage.objects.last()
        )
        included_test.save()

        return Response(status=status.HTTP_201_CREATED)
