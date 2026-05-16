import json
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import Student, ScanLog
from colorama import Fore, Style, Back

from colorama import init
init()

def mainpage(request):
    return render(request, 'QRCode_Main/mainpage.html')

@csrf_exempt
def scan(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'reason': 'Only POST allowed'})

    data = json.loads(request.body)
    token = data.get('qr_data') #This will get the token data from the HTML website.

    if not token:
        print(Style.BRIGHT + Fore.RED + "SERVER[+]: No token provided")
        return JsonResponse({'status': 'rejected', 'reason': 'No token provided'}) #I think this is a bit obvious.

    try:
        student = Student.objects.get(qr_token=token)  #This will get the data from the JSON file using the token. 
    except Student.DoesNotExist:
        print(Style.BRIGHT + Fore.RED + "SERVER[+]: Invalid QR code")
        return JsonResponse({'status': 'rejected', 'reason': 'Invalid QR code'})

    print("=== STUDENT FOUND ===")
    print(f"Name:        {student.student_name}")
    print(f"Year Group:  {student.year_group}")
    print(f"QR Token:    {student.qr_token}")
    print(f"Paid Penalty:  {student.paid_penalty}")
    print(f"Paid Keepy:    {student.paid_keepy}")
    print(f"Paid Sponges:  {student.paid_sponges}")
    print("=====================")

    return JsonResponse({'status': 'ok'})