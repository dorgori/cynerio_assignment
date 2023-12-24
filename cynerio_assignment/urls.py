"""cynerio_assignment URL Configuration

"""
from django.contrib import admin
from django.template.defaulttags import url
from django.urls import path, re_path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Your API",
        default_version='v1',
        description="Cynerio task",
        contact=openapi.Contact(email="dorgori7@gmail.com"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    re_path('admin/', admin.site.urls),
    path('core/', include('cynerio_assignment.core.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path("__debug__/", include("debug_toolbar.urls")),
]
