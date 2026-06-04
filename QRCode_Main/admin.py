from django.contrib import admin
from .models import Student, ScanLog, LoginDetails

admin.site.register(Student)
admin.site.register(ScanLog)
admin.site.register(LoginDetails)