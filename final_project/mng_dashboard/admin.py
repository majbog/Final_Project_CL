# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import Employee, TimeExp, Territory, Results, Productivity

# Register your models here.
admin.site.register(Employee)
admin.site.register(TimeExp)
admin.site.register(Territory)
admin.site.register(Results)
admin.site.register(Productivity)
