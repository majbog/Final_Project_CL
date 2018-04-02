import datetime
from dateutil.relativedelta import relativedelta
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import logout
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.generic.base import View
from django.views.generic.edit import UpdateView
from mng_dashboard.forms import NewEmployeeForm, LogInForm, TimeExpForm, AddTerritoryToEmployeeForm
from mng_dashboard.models import Employee, Territory
import numpy as np
import pandas as pd
from pandas.tseries import offsets
import plotly.offline as opy
import plotly.graph_objs as go
from sqlalchemy import create_engine

from .models import *

# Create your views here.

################## ADMIN #################################


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

            user = User.objects.filter(email=email).first()
            if user:
                user = authenticate(request, username=user.username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/results')

        ctx = {
            'form': form
        }
        return render(request, "login_form.html", ctx)


class LogOutView(View):
    def get(self, request):
        logout(request)
        return redirect(reverse("login"))


######################### EMPLOYEE ADMIN ##################################


class NewEmployeeView(LoginRequiredMixin, View):

    login_url = '/login'
    redirect_field_name = 'redirect_to'

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
                "active_employess": Employee.active_employees(),
                "all_territories": Territory.objects.all()
            }
            return render(request, "employee_form.html", ctx)


class ShowGeneralResults(LoginRequiredMixin, View):

    login_url = '/login'
    redirect_field_name = 'redirect_to'

    def get(self, request):

        # UNALLOCATED PART

        all_unallocated_results = UnallocatedResults.objects.all()
        desired_result_uncash =[]
        all_dates = [result.date for result in all_unallocated_results]
        all_dates.sort()
        desired_dates_uncash = all_dates[-30:]
        for date in desired_dates_uncash:
            uncash_amount = UnallocatedResults.objects.get(date=date)
            desired_result_uncash.append(float(uncash_amount.unallocated_cash))

        un_trace1 = go.Bar(
            x=desired_dates_uncash, y=desired_result_uncash, name="Unallocated Cash"
        )

        un_trace2 = go.Scatter(
            x=desired_dates_uncash, y=[250000] * len(desired_dates_uncash), name="SLA target"
        )

        uncash_data = [un_trace1, un_trace2]
        un_div = opy.plot(uncash_data, auto_open=False, output_type='div')



        # SET UP A DATE RANGE FOR ALL RESULTS

        all_reported_results = TerritoryResults.objects.all()
        all_reported_days = [result.date for result in all_reported_results]
        desired_dates = []

        for day in all_reported_days:
            if day not in desired_dates:
                desired_dates.append(day)
        desired_dates.sort()
        desired_dates = desired_dates[-30:]

        # GENERAL RESULTS:

        desired_gen_results = []

        for date in desired_dates:
            results = TerritoryResults.objects.filter(date=date)
            each_result_that_day = [result.result for result in results]
            general_result_that_day = sum(each_result_that_day)
            desired_gen_results.append(general_result_that_day)

        general_data = [go.Bar(
            x=desired_dates, y=desired_gen_results
        )]

        gen_div = opy.plot(general_data, auto_open=False, output_type='div')


        # GENERAL PRODUCTIVITY

        desired_prod_result =[]

        for date in desired_dates:
            results = Productivity.objects.filter(date=date)
            each_result_that_day=[result.number for result in results]
            general_result_that_day=sum(each_result_that_day)
            desired_prod_result.append(general_result_that_day)

        trace1 = go.Bar(
            x=desired_dates, y=desired_prod_result, name="All contacts per day"
        )

        trace2 = go.Scatter(
            x = desired_dates, y=[200]*len(desired_dates), name="SLA target"
        )

        trace3 = go.Scatter(
            x = desired_dates, y=[np.mean(desired_prod_result)]*len(desired_dates), name="Avarage"
        )


        prod_data = [trace1, trace2, trace3]
        prod_div = opy.plot(prod_data, auto_open=False, output_type='div')


        # HOW TO MEET SLAs

        this_month_prod =[]
        start_date = datetime.date.today().replace(day=1)
        dates_prod_month=[]
        for date in desired_dates:
            if date >= start_date:
                dates_prod_month.append(date)

        for date in dates_prod_month:
            results=Productivity.objects.filter(date=date)
            each_result_that_day=[result.number for result in results]
            general_prod_that_day = sum(each_result_that_day)
            this_month_prod.append(general_result_that_day)

        month_sla_target = 200*21

        prod_need_to_meet_slas = month_sla_target - sum(this_month_prod)

        end_of_month = datetime.date.today() + relativedelta(day=31)
        count_end_curr_month = np.busday_count(datetime.date.today(), end_of_month)

        avprod_to_meet_slas = prod_need_to_meet_slas/count_end_curr_month

        # SELECT BEST PERFORMERS

        best_performers =[]
        engine = create_engine('postgresql+psycopg2://postgres:coderslab@localhost/coll_db')
        prod_df = pd.read_sql_query(
            'SELECT "date", "number", "clerk_id" FROM mng_dashboard_productivity '
            'JOIN mng_dashboard_employee ON mng_dashboard_employee.id=mng_dashboard_productivity.clerk_id '
            'WHERE mng_dashboard_employee.active=True;',
            con=engine
        )
        table = pd.pivot_table(prod_df, values="number", index=["clerk_id"], columns=["date"], aggfunc=np.sum)
        mean_results = table[:].mean(axis=1)
        ordered = mean_results.sort_values(ascending=False)
        ids_best_perf = list(ordered.keys())[:3]
        for id in ids_best_perf:
            best_performers.append(Employee.objects.get(id=id))
        av_performance = sum(mean_results)/len(mean_results)

        request.session['ids_best_perf'] = ids_best_perf

        # CHECK MAIL STATUS

        all_mail_dates = [r.date for r in MailStatus.objects.all()]
        all_mail_dates.sort()

        sent_mails_to_show =[]
        received_mails_to_show =[]
        backlog_to_show=[]

        for date in all_mail_dates[-30:]:
            sent_mail = MailStatus.objects.get(date=date).sent
            sent_mails_to_show.append(sent_mail)
            received_mail = MailStatus.objects.get(date=date).received
            received_mails_to_show.append(received_mail)
            backloged = MailStatus.objects.get(date=date).backlog
            backlog_to_show.append(backloged)
            
        sm_trace = go.Bar(
            x=all_mail_dates[-30:], y= sent_mails_to_show, name='Sent eMails'
        )
        rm_trace= go.Bar(
            x=all_mail_dates[-30:], y= received_mails_to_show, name='Incoming eMails'
        )
        blog_trace = go.Bar(
            x=all_mail_dates[-30:], y=backlog_to_show, name='Backlog'
        )

        mail_data = [sm_trace, rm_trace, blog_trace]
        mail_div = opy.plot(mail_data, auto_open=False, output_type='div')

        backlog_atm = MailStatus.objects.get(date=all_mail_dates[-1]).backlog
        
        ftes_needed = backlog_atm/60




        ctx = {
            'prod_graph': prod_div,
            'gen_graph': gen_div,
            'un_graph': un_div,
            'best_performers':best_performers,
            "av_performance": str(round(av_performance)),
            "active_employees": Employee.active_employees(),
            "all_territories": Territory.objects.all(),
            "prod_slas": prod_need_to_meet_slas,
            "av_prod_for_slas": avprod_to_meet_slas,
            "mail_div": mail_div,
            "ftes_needed": round(ftes_needed,2)
            }

        return render(request, "general_results.html", ctx)



class ShowEmployeeView(LoginRequiredMixin, View):
    login_url = '/login'
    redirect_field_name = 'redirect_to'

    def get(self, request, employee_id):
        ids_bests = request.session.get('ids_best_perf', [])
        if int(employee_id) in ids_bests:
            is_best = True
        else:
            is_best = False

        employee = get_object_or_404(Employee, id=employee_id)
        today = datetime.date.today().strftime('%Y-%m-%d')

        # Territories part

        territories = Territory.objects.filter(clerks=Employee.objects.get(id=employee_id))

        # TimExpPart

        regular_amount_vac = 26
        vacations_to_be_taken = 0

        first_day_of_this_year = (datetime.date.today() - offsets.YearBegin()).strftime('%Y-%m-%d')
        last_day_of_this_year = (datetime.date.today() + offsets.YearEnd()).strftime('%Y-%m-%d')
        vacations_already_booked = len(TimeExp.objects.filter(clerk=employee_id, type=2, date__gte=first_day_of_this_year).filter(date__lte=last_day_of_this_year))
        vacations_to_be_taken = regular_amount_vac - vacations_already_booked



        all_vacations_to_happen = TimeExp.objects.filter(clerk=employee_id, type=2, date__gte=today)
        all_trainings_to_happen = TimeExp.objects.filter(clerk=employee_id, type=3, date__gte=today)

        # Productivity part

        clerk_inbound_call=[]
        clerk_outbound_call=[]
        clerks_outbound_mail=[]
        clerks_inbound_mail=[]
        all_clerk_productivity = Productivity.objects.filter(clerk=employee_id)
        all_dates_for_productivity = [result.date for result in all_clerk_productivity]
        desired_dates = []
        for date in all_dates_for_productivity:
            if date not in desired_dates:
                desired_dates.append(date)
        desired_dates.sort()
        desired_dates = desired_dates[-15:]
        for date in desired_dates:
            result_inbound_call = Productivity.objects.get(date=date, clerk=employee_id, type=1)
            clerk_inbound_call.append(int(result_inbound_call.number))
            result_outbound_call = Productivity.objects.get(date=date, clerk=employee_id, type=2)
            clerk_outbound_call.append(int(result_outbound_call.number))
            result_inbound_mail = Productivity.objects.get(date=date, clerk=employee_id, type=3)
            clerks_inbound_mail.append(int(result_inbound_mail.number))
            result_outbound_mail = Productivity.objects.get(date=date, clerk=employee_id, type=4)
            clerks_outbound_mail.append(int(result_outbound_mail.number))


        trace1 = go.Bar(
            x=desired_dates, y=clerk_inbound_call, name='Inbound Calls'
        )
        trace2 = go.Bar(
            x=desired_dates, y=clerk_outbound_call, name='Outbound Calls'
        )
        trace3 = go.Bar(
            x=desired_dates, y=clerks_inbound_mail, name='Inbound Mails'
        )
        trace4 = go.Bar(
            x=desired_dates, y=clerks_outbound_mail, name='Outbound Mails'
        )

        clerks_data = [trace1, trace2, trace3, trace4]
        layout = go.Layout(barmode='group', title='Productivity by Contact Type')

        fig = go.Figure(data=clerks_data, layout=layout)
        clerk_div = opy.plot(fig, auto_open=False, output_type='div')

        # productivity tendencies

        engine = create_engine('postgresql+psycopg2://postgres:coderslab@localhost/coll_db')
        prod_clerk_df = pd.read_sql_query(
            'SELECT "date", "number", "type" FROM mng_dashboard_productivity WHERE clerk_id={}' .format(employee_id), con=engine)
        
        av_clerks_in_call = prod_clerk_df[prod_clerk_df.type==1].number.mean()
        av_clerks_out_call = prod_clerk_df[prod_clerk_df.type==2].number.mean()
        # av_clerks_in_mail = prod_clerk_df[prod_clerk_df.type==3].number.mean()
        # av_clerks_out_mail = prod_clerk_df[prod_clerk_df.type==4].number.mean()
        

        ctx = {
            "employee": employee,
            "active_employees": Employee.active_employees(),
            "all_vacations_to_happen": all_vacations_to_happen,
            "all_trainings_to_happen": all_trainings_to_happen,
            "vacations_to_be_taken": vacations_to_be_taken,
            "territories": territories,
            "all_territories": Territory.objects.all(),
            "clerk_prod_graph": clerk_div,
            "is_best":is_best,
            "av_in_calls": round(av_clerks_in_call,2),
            "av_out_calls": round(av_clerks_out_call,2)
            

        }
        return render(request, "employee_details.html", ctx)


class DeactivateEmployeeView(LoginRequiredMixin, UpdateView):
    login_url = '/login'
    redirect_field_name = 'redirect_to'

    model = Employee
    fields = ('active',)
    template_name_suffix = 'deactivate_form'

    def get_success_url(self, **kwargs):
        return '/employee/{}/'.format(self.object.id)


class UpdateEmployeeView(LoginRequiredMixin, UpdateView):
    login_url = '/login'
    redirect_field_name = 'redirect_to'

    model = Employee
    fields = ("first_name", "last_name", "email", "active")
    template_name_suffix = '_update_form'

    def get_success_url(self, **kwargs):
        return '/employee/{}/' .format(self.object.id)


class ManageTimeView(LoginRequiredMixin, View):
    login_url = '/login'
    redirect_field_name = 'redirect_to'

    def get(self, request, employee_id):
        clerk = Employee.objects.get(id=employee_id)
        form = TimeExpForm(initial={
            "clerk": clerk.id
        })
        ctx={
            "form": form,
            "clerk": clerk.id,
            "active_employees": Employee.active_employees(),
            "all_territories": Territory.objects.all()
        }
        return render(request, 'time_exp_form.html', ctx)
    def post(self, request, employee_id):
        clerk = Employee.objects.get(id=employee_id)
        form = TimeExpForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data['date']
            type = form.cleaned_data['type']
            if not TimeExp.objects.filter(clerk=clerk, date=date).exists():
                item = TimeExp.objects.create(date=date, type=type, clerk=Employee.objects.get(id=employee_id))
            return redirect("/employee/{}" .format(employee_id))


def del_event_from_emp_profile(request, employee_id, event_id):
    event = TimeExp.objects.get(id=event_id)
    event.delete()
    return redirect('/employee/{}' .format(employee_id))


class UpdateTerritorySplit(LoginRequiredMixin, UpdateView):
    login_url = '/login'
    redirect_field_name = 'redirect_to'

    model = Territory
    fields = ("clerks",)
    template_name_suffix = '_split_form'

    def get_success_url(self, **kwargs):
        return '/results/territory/{}/' .format(self.object.id)

####################### COLL RESULTS


class ShowTerritoryView(LoginRequiredMixin, View):
    login_url = '/login'
    redirect_field_name = 'redirect_to'

    def get(self, request, territory_id):
        territory = Territory.objects.get(id=territory_id)
        clerks = territory.clerks.all()

        all_territory_results = TerritoryResults.objects.filter(territory=territory)
        all_dates = [result.date for result in all_territory_results]
        all_dates.sort()
        desired_dates_terr = all_dates[-30:]
        desired_results_terr = []
        for date in desired_dates_terr:
            result = TerritoryResults.objects.get(date=date, territory=territory)
            desired_results_terr.append(float(result.result))

        terr_data = [go.Bar(
            x=desired_dates_terr, y=desired_results_terr
        )]

        terr_div = opy.plot(terr_data, auto_open=False, output_type='div')

        ctx = {
            'terr_graph': terr_div,
            "active_employees": Employee.active_employees(),
            "all_territories": Territory.objects.all(),
            "territory": territory,
            "clerks": clerks
            }

        return render(request, "territory_details.html", ctx)


class ShowTimeExpView(LoginRequiredMixin, View):

    login_url = '/login'
    redirect_field_name = 'redirect_to'

    def get(self,request):

        today = datetime.date.today().strftime('%Y-%m-%d')
        all_absences_to_be_taken = TimeExp.objects.filter(date__gt=today).exclude(type=4).order_by("date")
        all_absences_to_be_taken.values()
        absences_list = [
            {'date': ab.date, 'clerk': ab.clerk.name, 'type': ab.get_type_display()}
            for ab in all_absences_to_be_taken
        ]
        ctx = {
            "clerks": absences_list,
            "active_employees": Employee.active_employees(),
            "all_territories": Territory.objects.all(),
        }
        return render(request, "show_absences.html", ctx)







