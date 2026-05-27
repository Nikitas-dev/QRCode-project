from django.db import models


class Student(models.Model):
    qr_token = models.CharField(max_length=1000, unique=True)
    student_name = models.CharField(max_length=100, blank=True)
    year_group = models.CharField(max_length=10, blank=True)
    form_group = models.CharField(max_length=20, blank=True)
    issued_date = models.DateTimeField(null=True, blank=True)
    issued_by = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.student_name or self.qr_token


class ScanLog(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    activity = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student} - {self.activity}"


class LoginDetails(models.Model):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)