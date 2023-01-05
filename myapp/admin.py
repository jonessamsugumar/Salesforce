# from django.contrib import admin
# from .models import Req, Adminmodel


# from .models import Task
# from .models import approver
# from .models import Program
# from .models import VP_Approval

"""

@admin.register(Req)
class RequestAdmin(admin.ModelAdmin):
    list_display = ('request_name', 'program')
    ordering = ('request_name',)
    search_fields = ('request_name', 'program')

@admin.register(Adminmodel)
class AdminProfile(admin.ModelAdmin):
    list_display = ('admin_id', 'admin_name','admin_email','admin_program')
    ordering = ('admin_id',)
    search_fields = ('admin_name', 'program')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('request_name', 'status')
    ordering = ('request_name',)

@admin.register(approver)
class approversAdmin(admin.ModelAdmin):
    list_display = ('program','name')
    ordering = ('program',)


@admin.register(Program)
class approversAdmin(admin.ModelAdmin):
    list_display = ('program_id','name')
    ordering = ('program_id',)

@admin.register(VP_Approval)
class approversAdmin(admin.ModelAdmin):
    list_display = ('program','name')
    ordering = ('program',)
"""
