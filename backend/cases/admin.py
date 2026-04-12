from django.contrib import admin

from .models import Case, CaseAssignment, CaseLog, CaseStatus, Category, Subclinic

admin.site.register(Subclinic)
admin.site.register(Category)
admin.site.register(CaseStatus)
admin.site.register(Case)
admin.site.register(CaseAssignment)
admin.site.register(CaseLog)
