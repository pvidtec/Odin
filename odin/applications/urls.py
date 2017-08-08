from django.conf.urls import url

from .views import (
    CreateApplicationInfoView,
    EditApplicationInfoView,
    CreateIncludedApplicationTaskView,
    ApplyToCourseView,
    UserApplicationsListView,
    EditApplicationView,
    AddIncludedApplicationTaskFromExistingView
)

urlpatterns = [
    url(regex='^(?P<course_id>[0-9]+)/create-application-info/$',
        view=CreateApplicationInfoView.as_view(),
        name='create-application-info'),
    url(regex='^(?P<course_id>[0-9]+)/edit-application-info/$',
        view=EditApplicationInfoView.as_view(),
        name='edit-application-info'),
    url(regex='^(?P<course_id>[0-9]+)/add-application-task/$',
        view=CreateIncludedApplicationTaskView.as_view(),
        name='add-application-task'),
    url(regex='^(?P<course_id>[0-9]+)/apply/$',
        view=ApplyToCourseView.as_view(),
        name='apply-to-course'),
    url(regex='^user-applications/$',
        view=UserApplicationsListView.as_view(),
        name='user-applications'),
    url(regex='^(?P<course_id>[0-9]+)/edit-application/$',
        view=EditApplicationView.as_view(),
        name='edit-application'),
    url(regex='^(?P<course_id>[0-9]+)/existing-application-tasks/$',
        view=AddIncludedApplicationTaskFromExistingView.as_view(),
        name='add-application-task-from-existing'),
]