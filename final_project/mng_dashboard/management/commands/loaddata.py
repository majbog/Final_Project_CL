from django.core.management.base import BaseCommand, CommandError
import pandas as pd
from mng_dashboard.models import Employee, TerritoryResults, UnallocatedResults, Territory, Productivity
import datetime



class Command(BaseCommand):
    help = 'Command to do........'

    def handle(self, *args, **options):
        try:

            # GET DATE

            date_df = pd.read_excel("/Users/majbog/workspace/Data Source/sample_xls1.xls", sheet_name="date")

            reported_date = date_df.loc[0,"Date"].strftime('%Y-%m-%d')

            if reported_date > datetime.date.today().strftime('%Y-%m-%d'):
                print("Can't report future dates!")

            if Productivity.objects.filter(date=reported_date).exists():
                print("There's already an report with a date {} given" .format(reported_date))


            # GET EMPLOYEES' PRODUCTIVITY RESULTS

            productivity_df = pd.read_excel("/Users/majbog/workspace/Data Source/sample_xls1.xls",
                                            sheet_name="productivity", index_col="GLID")

            reported_clerks = productivity_df.index.tolist()
            empl_atm = Employee.objects.all()
            employees_list = []
            for em in empl_atm:
                employees_list.append(em.int_id)
            for r_e in reported_clerks:
                if r_e in employees_list:
                    clerk_inbound_call = productivity_df.loc[r_e, "InboundCall"]
                    clerk_inbound_mail = productivity_df.loc[r_e, "InboundMail"]
                    clerk_outbound_call = productivity_df.loc[r_e, "OutboundCall"]
                    clerk_outbound_mail = productivity_df.loc[r_e, "OutboundMail"]
                    item_inbound_call = Productivity.objects.create(clerk=Employee.objects.get(int_id=r_e),
                                                                    date=reported_date, type=1, number=clerk_inbound_call)
                    item_inbound_mail = Productivity.objects.create(clerk=Employee.objects.get(int_id=r_e),
                                                                    date=reported_date, type=3, number=clerk_inbound_mail
                                                                    )
                    item_outbound_call = Productivity.objects.create(clerk=Employee.objects.get(int_id=r_e),
                                                                     date=reported_date, type=2, number=clerk_outbound_call
                                                                     )
                    item_outbound_mail = Productivity.objects.create(clerk=Employee.objects.get(int_id=r_e),
                                                                     date=reported_date, type=4, number=clerk_outbound_mail
                                                                     )

            # DAY RESULTS

            day_results_df = pd.read_excel("/Users/majbog/workspace/Data Source/sample_xls1.xls",
                                           sheet_name="day_results", index_col="Territory"
                                           )

            # DAY RESULTS BY TERRITORY

            reported_territories = day_results_df.index.tolist()
            territories = Territory.list_terr_names()

            for terr in reported_territories:
                if terr in territories:
                    terr_day_result = day_results_df.loc[terr, "Amount"]
                    TerritoryResults.objects.create(date=reported_date, result=terr_day_result,
                                                    territory=Territory.objects.get(name=terr)
                                                    )

            # DAY RESULTS - UNALLOCATED CASH

            unalloc_day_result = day_results_df.loc["Unallocated", "Amount"]
            UnallocatedResults.objects.create(date=reported_date, unallocated_cash=unalloc_day_result)




        except Exception as e:
            CommandError(repr(e))