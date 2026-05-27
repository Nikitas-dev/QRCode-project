from django.db import models

class Student(models.Model):
    qr_token = models.CharField(max_length=1000, unique=True, blank=True)
    student_name = models.CharField(max_length=100, blank=True)
    year_group = models.CharField(max_length=10, blank=True)
    issued_date = models.DateTimeField(blank=True)
    issued_by = models.CharField(max_length=50, blank=True)

class ScanLog(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    activity = models.CharField(max_length=100) 
    timestamp = models.DateTimeField(auto_now_add=True)

class login_details(models.Model):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)