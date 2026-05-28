import json

from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import Student, ScanLog

def login_view(request):
    return render(request, "Login.html")

def mainpage(request):
    return render(request, "QRCode_Main/mainpage.html")


@csrf_exempt
@require_POST
def scan(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({
            "status": "error",
            "reason": "Invalid JSON"
        }, status=400)

    token = data.get("qr_data")

    if not token:
        return JsonResponse({
            "status": "rejected",
            "reason": "No QR token provided"
        }, status=400)

    student = Student.objects.filter(qr_token=token).first()

    if not student:
        return JsonResponse({
            "status": "unregistered",
            "reason": "This QR code has no student details yet",
            "qr_data": token
        })

    if not student.student_name:
        return JsonResponse({
            "status": "empty",
            "reason": "This QR code exists but student details have not been added yet",
            "qr_data": token
        })

    ScanLog.objects.create(
        student=student,
        activity="QR scanned"
    )

    return JsonResponse({
        "status": "ok",
        "student": {
            "name": student.student_name,
            "year_group": student.year_group,
            "form_group": student.form_group,
            "qr_token": student.qr_token,
        }
    })


@csrf_exempt
@require_POST
def submit_details(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "reason": "Invalid JSON"
        }, status=400)

    qr_data = data.get("qr_data")
    name = data.get("name")
    year_group = data.get("year_group")
    form_group = data.get("form_group")

    if not qr_data or not name or not year_group or not form_group:
        return JsonResponse({
            "success": False,
            "reason": "Missing required fields"
        }, status=400)

    student, created = Student.objects.get_or_create(
        qr_token=qr_data,
        defaults={
            "issued_date": timezone.now()
        }
    )

    student.student_name = name
    student.year_group = year_group
    student.form_group = form_group

    if not student.issued_date:
        student.issued_date = timezone.now()

    student.save()

    ScanLog.objects.create(
        student=student,
        activity="Student details submitted"
    )

    return JsonResponse({
        "success": True,
        "created": created,
        "student": {
            "name": student.student_name,
            "year_group": student.year_group,
            "form_group": student.form_group,
            "qr_token": student.qr_token,
        }
    })