from django.contrib import admin

from .models import Case, CaseAssignment, CaseLog, CaseStatus, Category, Subclinic, CaseCancellationRequest

@admin.register(CaseCancellationRequest)
class CaseCancellationRequestAdmin(admin.ModelAdmin):
    list_display = ('case', 'requested_by', 'status', 'created_at', 'reviewed_at')
    list_filter = ('status', 'created_at')
    search_fields = ('case__description', 'requested_by__username', 'reason')
    readonly_fields = ('created_at', 'reviewed_at')

admin.site.register(Subclinic)
admin.site.register(Category)
admin.site.register(CaseStatus)
admin.site.register(Case)
admin.site.register(CaseAssignment)
admin.site.register(CaseLog)
