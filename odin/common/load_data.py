import json
from copy import deepcopy

from datetime import timedelta
from dateutil import parser

from django.apps import apps

from allauth.account.models import EmailAddress

from odin.users.models import BaseUser
from odin.education.models import Course, Student, Teacher, Week, Material, Topic
from odin.education.services import add_student, add_teacher


class BaseLoader:
    """ field_mapping = [(modelfield, dictfield), (modelfield, dictfield), ... ] """

    json_model = None
    django_model = None
    json_fields = []
    model_fields = []

    def __init__(self, source='odin/common/dump.json'):
        self.source = source
        self.data = self.load_data()

    def load_data(self):
        with open(self.source, 'r') as source:
            data = json.load(source)

        result = []
        for item in data:
            if item['model'] == self.json_model:
                result.append(item)
        return result

    def get_fields(self):
        return self.data[0]['fields'].keys()

    def get_field_mapping(self):
        mapping = [i for i in zip(self.model_fields, self.json_fields)]

        for item in self.data:
            kwargs = {pair[0]: item['fields'].get(pair[1]) for pair in mapping}
            kwargs['id'] = item['pk']
            yield kwargs

    def generate_orm_objects(self):
        instance_list = []

        for kwargs in self.get_field_mapping():
            instance = self.django_model(**kwargs)
            instance_list.append(instance)
        return self.django_model.objects.bulk_create(instance_list)

    def __str__(self):
        return str(self.get_fields())


class CourseDescriptionLoader(BaseLoader):
    json_model = 'website.coursedescription'
    django_model = apps.get_model('education.CourseDescription')
    model_fields = ['course', 'verbose']
    json_fields = ['course', 'list_courses_text']

    def get_field_mapping(self):
        CourseModel = apps.get_model('education.Course')
        for kwargs in super().get_field_mapping():
            final_kwargs = deepcopy(kwargs)
            final_kwargs['course'] = CourseModel.objects.get(id=kwargs['course'])
            yield final_kwargs


class CourseLoader(BaseLoader):
    json_model = 'education.course'
    django_model = apps.get_model('education.Course')
    model_fields = [
        'name',
        'start_date',
        'end_date',
        'repository',
        'video_channel',
        'facebook_group'
    ]
    json_fields = [
        'name',
        'start_time',
        'end_time',
        'git_repository',
        'video_channel',
        'fb_group'
    ]

    def generate_orm_objects(self):
        descriptions_data = CourseDescriptionLoader()
        data = descriptions_data.load_data()

        instance_list = []

        for kwargs in self.get_field_mapping():
            final_kwargs = deepcopy(kwargs)
            for cd in data:
                if cd['fields']['course'] == kwargs['id']:
                    final_kwargs['slug_url'] = cd['fields']['url']
                    instance = self.django_model(**final_kwargs)
                    instance.start_date = parser.parse(instance.start_date)
                    instance.end_date = parser.parse(instance.end_date)
                    instance_list.append(instance)

        courses = self.django_model.objects.bulk_create(instance_list)
        weeks = []
        for course in courses:
            week_count = course.duration_in_weeks
            start_date = course.start_date
            start_date = start_date - timedelta(days=start_date.weekday())

            for i in range(1, week_count + 1):
                current = Week(course=course,
                               number=i,
                               start_date=start_date,
                               end_date=start_date + timedelta(days=7))
                start_date = current.end_date
                weeks.append(current)
        Week.objects.bulk_create(weeks)
        descriptions_data.generate_orm_objects()


class TeacherLoader(BaseLoader):
    json_model = 'education.teacher'
    django_model = apps.get_model('education.Teacher')
    model_fields = ['user']
    json_fields = ['pk']

    def generate_orm_objects(self):
        for kwargs in self.get_field_mapping():
            user = BaseUser.objects.get(pk=kwargs['id'])
            self.django_model.objects.create_from_user(user)


class StudentLoader(BaseLoader):
    json_model = 'education.student'
    django_model = apps.get_model('education.Student')
    model_fields = ['user']
    json_fields = ['pk']

    def generate_orm_objects(self):
        for kwargs in self.get_field_mapping():
            user = BaseUser.objects.get(pk=kwargs['id'])
            if not user.password:
                user.set_unusable_password()
            self.django_model.objects.create_from_user(user)


class BaseUserLoader(BaseLoader):
    json_model = 'base_app.baseuser'
    django_model = apps.get_model('users.BaseUser')
    model_fields = ['email', 'is_active', 'is_staff', 'is_superuser', 'password']
    json_fields = ['email', 'is_active', 'is_staff', 'is_superuser', 'password']

    def generate_orm_objects(self):
        users = super().generate_orm_objects()
        for user in users:
            if user.is_active:
                EmailAddress.objects.create(
                    user=user,
                    email=user.email,
                    verified=True,
                    primary=True
                )


class ProfileLoader(BaseLoader):
    json_model = 'base_app.baseuser'
    django_model = apps.get_model('users.Profile')
    model_fields = [
        'full_name',
        'full_name_ph',
        'description',
        'works_at',
        'studies_at',
        'avatar',
        'full_image',
        'cropping'
    ]
    json_fields = [
        'first_name',
        'last_name',
        'description',
        'works_at',
        'studies_at',
        'avatar',
        'full_image',
        'cropping'
    ]

    def get_field_mapping(self):
        for kwargs in super().get_field_mapping():
            final_kwargs = deepcopy(kwargs)
            final_kwargs['full_name'] = final_kwargs.pop('full_name', None) +\
                ' ' + final_kwargs.pop('full_name_ph', None)
            yield final_kwargs

    def generate_orm_objects(self):
        instance_list = []
        for kwargs in self.get_field_mapping():
            kwargs['user'] = BaseUser.objects.get(pk=kwargs.pop('id', None))
            instance_list.append(self.django_model(**kwargs))
        self.django_model.objects.bulk_create(instance_list)
        return instance_list


class CourseAssignmentLoader(BaseLoader):
    json_model = 'education.courseassignment'
    django_model = apps.get_model('education.CourseAssignment')
    model_fields = ['course', 'student']
    json_fields = ['course', 'user']

    def generate_orm_objects(self):
        for kwargs in self.get_field_mapping():
            course_qs = Course.objects.filter(id=kwargs.get('course'))
            student_qs = Student.objects.filter(id=kwargs.get('student'))
            if course_qs.exists() and student_qs.exists():
                course = course_qs.first()
                student = student_qs.first()
                if student and course:
                    add_student(course, student)

        teacher_loader = TeacherLoader()
        teacher_loader.load_data()

        for item in teacher_loader.data:
            teacher_qs = Teacher.objects.filter(id=item.get('pk'))
            if teacher_qs.exists():
                teacher = teacher_qs.first()
                for course_id in item['fields'].get('teached_courses'):
                    course_qs = Course.objects.filter(id=course_id)
                    if course_qs.exists():
                        course = course_qs.first()
                    else:
                        continue
                    if teacher and course:
                        add_teacher(course, teacher)


class TopicLoader(BaseLoader):
    json_model = 'education.material'
    django_model = apps.get_model('education.Topic')
    model_fields = ['week', 'course', 'name']
    json_fields = ['week', 'course', 'title']

    def generate_orm_objects(self):
        instance_list = []
        for kwargs in self.get_field_mapping():
            course_qs = Course.objects.filter(id=kwargs.get('course'))
            if course_qs.exists():
                course = course_qs.first()
                week_qs = Week.objects.filter(course=course, number=kwargs.get('week'))
                if week_qs.exists():
                    week = week_qs.first()
                    kwargs['course'] = course
                    kwargs['week'] = week
                    instance = self.django_model(**kwargs)
                    instance_list.append(instance)
        self.django_model.objects.bulk_create(instance_list)
        return instance_list


class IncludedMaterialLoader(BaseLoader):
    json_model = 'education.material'
    django_model = apps.get_model('education.IncludedMaterial')
    model_fields = ['identifier', 'content']
    json_fields = ['title', 'description']

    def generate_orm_objects(self):
        instance_list = []
        for kwargs in self.get_field_mapping():
            id = kwargs.pop('id')
            material = Material.objects.create(**kwargs)
            topic_qs = Topic.objects.filter(pk=id)
            if topic_qs.exists():
                topic = topic_qs.first()
                instance = self.django_model(topic=topic, material=material)
                instance.__dict__.update(material.__dict__)
                instance_list.append(instance)

        self.django_model.objects.bulk_create(instance_list)
        return instance_list