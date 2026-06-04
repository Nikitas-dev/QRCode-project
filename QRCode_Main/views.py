import json
import csv
from pathlib import Path

from django.db.models import Count, Max
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import Student, ScanLog, LoginDetails


def clean_form_group(form_group):
    form = (form_group or "").strip().lower()

    if form in ["oscar romero", "romero", "romeo"]:
        return "Oscar Romero"

    if form in [
        "bernadette soubirous",
        "bernedette soubirous",
        "bernedette subirous",
        "soubirous",
        "subirous",
    ]:
        return "Bernadette Soubirous"

    if form in ["john bosco", "bosco"]:
        return "John Bosco"

    if form in ["john paul", "john paul ii"]:
        return "John Paul"

    if form in ["carlo acutis", "acutis"]:
        return "Carlo Acutis"

    if form in ["bakhita", "bhakita", "bakitha"]:
        return "Bakhita"

    return form_group or ""


def get_year_number(year_group):
    digits = "".join(filter(str.isdigit, year_group or ""))

    if digits:
        return int(digits)

    return 999


def update_qr_spreadsheet():
    spreadsheet_path = Path("qr_token_details.csv")

    students = Student.objects.annotate(
        scan_count=Count("scanlog"),
        last_scanned=Max("scanlog__timestamp")
    )

    form_order = {
        "Oscar Romero": 1,
        "Bernadette Soubirous": 2,
        "John Bosco": 3,
        "John Paul": 4,
        "Carlo Acutis": 5,
        "Bakhita": 6,
    }

    def sort_student(student):
        cleaned_form = clean_form_group(student.form_group)

        return (
            get_year_number(student.year_group),
            form_order.get(cleaned_form, 999),
            cleaned_form.lower(),
            student.student_name.lower()
        )

    students = sorted(students, key=sort_student)

    with open(spreadsheet_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow([
            "QR Token",
            "Student Name",
            "Year Group",
            "Form Group",
            "Issued Date",
            "Issued By",
            "Scan Count",
            "Last Scanned",
            "Status",
        ])

        for student in students:
            status = "Used" if student.student_name else "Unused"

            writer.writerow([
                student.qr_token,
                student.student_name,
                student.year_group,
                clean_form_group(student.form_group),
                student.issued_date,
                student.issued_by,
                student.scan_count,
                student.last_scanned,
                status,
            ])


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        login_correct = LoginDetails.objects.filter(
            username=username,
            password=password
        ).exists()

        if login_correct:
            request.session["logged_in"] = True
            request.session["username"] = username
            return redirect("mainpage")

        return render(request, "QRCode_Main/Login.html", {
            "error": "Invalid stall name or password"
        })

    return render(request, "QRCode_Main/Login.html")


def mainpage(request):
    if not request.session.get("logged_in"):
        return redirect("login")

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
            "status": "rejected",
            "reason": "This QR code is not in the database"
        }, status=404)

    if not student.student_name:
        ScanLog.objects.create(
            student=student,
            activity="Blank QR scanned"
        )

        update_qr_spreadsheet()

        return JsonResponse({
            "status": "empty",
            "reason": "This QR code exists but student details have not been added yet",
            "qr_data": token
        })

    ScanLog.objects.create(
        student=student,
        activity="QR scanned"
    )

    update_qr_spreadsheet()

    return JsonResponse({
        "status": "ok",
        "student": {
            "name": student.student_name,
            "year_group": student.year_group,
            "form_group": clean_form_group(student.form_group),
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

    student = Student.objects.filter(qr_token=qr_data).first()

    if not student:
        return JsonResponse({
            "success": False,
            "reason": "This QR code is not in the database"
        }, status=404)

    if student.student_name:
        return JsonResponse({
            "success": False,
            "reason": "This QR code already has details saved"
        }, status=400)

    student.student_name = name
    student.year_group = year_group
    student.form_group = clean_form_group(form_group)
    student.issued_date = timezone.now()

    if request.session.get("username"):
        student.issued_by = request.session.get("username")

    student.save()

    ScanLog.objects.create(
        student=student,
        activity="Student details submitted"
    )

    update_qr_spreadsheet()

    return JsonResponse({
        "success": True,
        "created": False,
        "student": {
            "name": student.student_name,
            "year_group": student.year_group,
            "form_group": clean_form_group(student.form_group),
            "qr_token": student.qr_token,
        }
    })