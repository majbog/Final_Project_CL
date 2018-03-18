"""final_project URL Configuration

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
from django.conf.urls import url
from django.contrib import admin
from mng_dashboard.views import LogInView, NewEmployeeView, ShowResults, ShowEmployeeView, \
    UpdateEmployeeView, ManageTimeView

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^main/$', ShowResults.as_view(), name='main'),
    url(r'^login/$', LogInView.as_view(), name="login"),
    url(r'^employee/new/$', NewEmployeeView.as_view(), name='new-employee'),
    url(r'^employee/(?P<employee_id>(\d+))/$', ShowEmployeeView.as_view(), name='employee-details'),
    url(r'^employee/(?P<pk>(\d+))/update/$', UpdateEmployeeView.as_view(), name='update-employee'),
    url(r'^employee/(?P<employee_id>(\d+))/time_manager/$', ManageTimeView.as_view(), name='time-manager')
]
