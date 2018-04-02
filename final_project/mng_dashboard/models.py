from django.db import models
from django.core.exceptions import ValidationError
import re


# COLL_GROUPS =(
#     (1, "Madrid"),
#     (2, "Barcelona"),
#     (3, "Valencia"),
#     (4, "Alicante"),
#     (5, "Bilbao"),
#     (6, "Zaragoza"),
#     (7, "Malaga"),
#     (8, "Sevilla"),
#     (9, "GLOBAL")
# )
#
# COLL_CODES =(
#     (1, "MAD"),
#     (2, "BCN"),
#     (3, "VLC"),
#     (4, "ALC"),
#     (5, "BIO"),
#     (6, "ZAZ"),
#     (7, "AGP"),
#     (8, "SVQ"),
#     (9, "OVERDUE RECEIVABLES")
# )

TIME_EXP_TYPES = (
    (1, "Sick Leave"),
    (2, "Vacation"),
    (3, "Training"),
    (4, "Overtime")
)

# CONTACT_RESULTS = (
#     (1, "Customer Reached"),
#     (2, "Customer Not Reached"),
#     (3, "Try Again Later"),
#     (4, "Message Left")
# )

CONTACT_TYPES = (
    (1, "Inbound call"),
    (2, "Outbound call"),
    (3, "Inbound email"),
    (4, "Outbound email")
)

def validate_emp_mail(mail):
    reg = re.compile('^[A-Za-z0-9._%+-]+@emp_mail.com$')
    if not reg.match(mail):
        raise ValidationError("The correct domain for employee's email is @emp_mail.com")


# Create your models here.


class Employee(models.Model):
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    email = models.CharField(max_length=64, validators=[validate_emp_mail])
    active = models.NullBooleanField(default=True)
    int_id = models.CharField(max_length=8)

    @property
    def name(self):
        return "{} {}".format(self.first_name, self.last_name)

    def __str__(self):
        return self.name

    @staticmethod
    def active_employees():
        active_employees = Employee.objects.filter(active=True)
        return active_employees


class Territory(models.Model):
    name = models.CharField(max_length=64)
    clerks = models.ManyToManyField(Employee)

    @staticmethod
    def list_terr_names():
        territories_names = []
        for ter in Territory.objects.all():
            territories_names.append(ter.name)
        return territories_names


class TimeExp(models.Model):
    date = models.DateField()
    type = models.IntegerField(choices=TIME_EXP_TYPES)
    clerk = models.ForeignKey(Employee, on_delete=None)

    def __str__(self):
        return "{}" .format(self.clerk.name)


class TerritoryResults(models.Model):
    date = models.DateField()
    territory = models.ForeignKey(Territory, on_delete=None)
    result = models.DecimalField(max_digits=15, decimal_places=2)


class UnallocatedResults(models.Model):
    date = models.DateField()
    unallocated_cash = models.DecimalField(max_digits=15, decimal_places=2)


class Productivity(models.Model):
    date = models.DateField()
    clerk = models.ForeignKey(Employee, on_delete=None)
    number = models.IntegerField()
    # result = models.IntegerField(choices=CONTACT_RESULTS)
    type = models.IntegerField(choices=CONTACT_TYPES)


class MailStatus(models.Model):
    date = models.DateField()
    sent = models.IntegerField()
    received = models.IntegerField()
    backlog = models.IntegerField()
