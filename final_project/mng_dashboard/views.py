from django.contrib.auth import authenticate
from django.contrib.auth.views import login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.base import View
from mng_dashboard.forms import NewEmployeeForm, LogInForm, TimeExpForm
from mng_dashboard.models import Employee

from .models import *

# Create your views here.

class LogInView(View):
    def get(self, request):
        form = LogInForm()
        ctx = {
            'form': form
        }
        return render(request, "login_form.html", ctx)

    def post(self, request):
        form = LogInForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(username=User.objects.get(email=email), password=password)
            if user is not None:
                login(request, user)
                return redirect('main')
            else:
                ctx = {
                    'form': form
                }
                return render(request, "login_form.html", ctx)


class ShowResults(View):
    def get(self, request):
        pass


class NewEmployeeView(View):

    def get(self, request):
        form = NewEmployeeForm()
        ctx = {
            "form": form,
            "active_employees": Employee.active_employees()
        }
        return render(request, "employee_form.html", ctx)

    def post(self, request):
        form = NewEmployeeForm(request.POST)
        if form.is_valid():
            employee = form.save()
            return redirect("/employee/{}" .format(employee.id))
        else:
            ctx ={
                "form": form,
                "active_employess": Employee.active_employees()
            }
            return render(request, "employee_form.html", ctx)



class ShowEmployeeView(View):
    def get(self, request, employee_id):
        employee = get_object_or_404(Employee, id=employee_id)
        ctx = {
            "employee": employee,
            "active_employees": Employee.active_employees()
        }
        return render(request, "employee_details.html", ctx)

class UpdateEmployeeView(View):
    pass


class ManageTimeView(View):
    def get(self, request, employee_id):
        clerk = Employee.objects.get(id = employee_id)
        form = TimeExpForm()
        ctx={
            "form": form,
            "clerk": employee_id,
            "active_employees": Employee.active_employees()
        }
        return render(request, 'time_exp_form.html', ctx)
    def post(self, request, employee_id):
        form = TimeExpForm(request.POST)
        if form.is_valid:
            date = form.cleaned_data['date']
            type = form.cleaned_data['type']
            item = TimeExp.objects.create(clerk=employee_id, date=date, type=type)
            return redirect("/employee/{}" .format(employee_id))


