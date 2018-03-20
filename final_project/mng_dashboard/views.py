import datetime
from django.contrib.auth import authenticate
from django.contrib.auth.views import login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.base import View
from mng_dashboard.forms import NewEmployeeForm, LogInForm, TimeExpForm
from mng_dashboard.models import Employee
from pandas.tseries import offsets

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
        today = datetime.date.today().strftime('%Y-%m-%d')

        # Territories part

        territories = Territory.objects.filter(clerks=Employee.objects.get(id=employee_id))

        # TimExpPart

        regular_amount_vac = 26
        vacations_to_be_taken = 0

        first_day_of_this_year = (datetime.date.today() - offsets.YearBegin()).strftime('%Y-%m-%d')
        last_day_of_this_year = (datetime.date.today() + offsets.YearEnd()).strftime('%Y-%m-%d')
        vacations_already_booked = len(TimeExp.objects.filter(clerk=employee_id, date__gte=first_day_of_this_year).filter(date__lte=last_day_of_this_year))
        vacations_to_be_taken = regular_amount_vac - vacations_already_booked



        all_vacations_to_happen = TimeExp.objects.filter(clerk=employee_id, type=2, date__gte=today)
        all_trainings_to_happen = TimeExp.objects.filter(clerk=employee_id, type=3, date__gte=today)


        ctx = {
            "employee": employee,
            "active_employees": Employee.active_employees(),
            "all_vacations_to_happen": all_vacations_to_happen,
            "all_trainings_to_happen": all_trainings_to_happen,\
            "vacations_to_be_taken": vacations_to_be_taken,
            "territories": territories

        }
        return render(request, "employee_details.html", ctx)

class UpdateEmployeeView(View):
    pass


class ManageTimeView(View):
    def get(self, request, employee_id):
        clerk = Employee.objects.get(id=employee_id)
        form = TimeExpForm(initial={
            "clerk": clerk.id
        })
        ctx={
            "form": form,
            "clerk": clerk.id,
            "active_employees": Employee.active_employees()
        }
        return render(request, 'time_exp_form.html', ctx)
    def post(self, request, employee_id):
        clerk = Employee.objects.get(id=employee_id)
        form = TimeExpForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data['date']
            type = form.cleaned_data['type']
            if not TimeExp.objects.filter(clerk=Employee.objects.get(id=employee_id), date=date).exists():
                item = TimeExp.objects.create(date=date, type=type, clerk=Employee.objects.get(id=employee_id))
            return redirect("/employee/{}" .format(employee_id))


class DeleteEventView(View):
    pass