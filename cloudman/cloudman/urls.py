"""
CloudMan URL Configuration.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import include
from django.conf.urls import url
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(title="Cloudman API", default_version="v1"),
   urlconf='cloudman.urls',
   url=settings.REST_SCHEMA_BASE_URL,
)

urlpatterns = [
    url(r'^cloudman/cloudlaunch/cloudlaunch/api/v1/auth/user/', include('cloudlaunchserver.urls')),
    url(r'^cloudman/', include('cloudlaunchserver.urls')),
    url(r'^cloudman/api/v1/', include('clusterman.urls')),
    url(r'^cloudman/api/v1/', include('helmsman.urls')),
    url(r'^cloudman/api/v1/', include('projman.urls')),
    url(r'^cloudman/api/v1/schema/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^cloudman/openid/', include('djangooidc.urls')),
]

# Uncomment to have Gunicorn serve static content (dev only)
# Also run: python manage.py collectstatic
# from django.contrib.staticfiles.urls import staticfiles_urlpatterns
# urlpatterns += staticfiles_urlpatterns()
