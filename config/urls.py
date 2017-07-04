from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView
from django.views import defaults as default_views
from allauth import urls
from allauth.socialaccount import urls
from odin.dashboard.views import RedirectToDashboardIndexView
from odin.education.urls import courses_public_urlpatterns

urlpatterns = [
    url(settings.ADMIN_URL, admin.site.urls),
    url(r'^$', RedirectToDashboardIndexView.as_view()),
    url(r'^public/', include(courses_public_urlpatterns, namespace='public')),
    url(r'^auth/', include('odin.authentication.urls')),
    url(r'^dashboard/', include('odin.dashboard.urls', namespace='dashboard')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        url(r'^400/$', default_views.bad_request, kwargs={'exception': Exception('Bad Request!')}),
        url(r'^403/$', default_views.permission_denied, kwargs={'exception': Exception('Permission Denied')}),
        url(r'^404/$', default_views.page_not_found, kwargs={'exception': Exception('Page not Found')}),
        url(r'^500/$', default_views.server_error),
    ]
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            url(r'^__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns