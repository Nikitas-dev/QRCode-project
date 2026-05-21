from django.db import models

class Student(models.Model):
    qr_token = models.CharField(max_length=1000, unique=True)
    student_name = models.CharField(max_length=100)
    year_group = models.CharField(max_length=10)


class ScanLog(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    activity = models.CharField(max_length=100)  # "penalty", "keepy", "sponges"
    timestamp = models.DateTimeField(auto_now_add=True)