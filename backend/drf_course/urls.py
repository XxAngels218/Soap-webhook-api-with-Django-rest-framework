from django.urls import path
from django.contrib import admin
from core import views as core_views
from rest_framework import routers
from django.urls import path
from core.views import soap_view
from core.views import webhook



router = routers.DefaultRouter()

urlpatterns = router.urls

urlpatterns += [
    path('admin/', admin.site.urls),
    path('contact/', core_views.ContactAPIView.as_view()),
    path('soap/', soap_view, name='soap'),
    path('webhook/', webhook, name='webhook'),
]