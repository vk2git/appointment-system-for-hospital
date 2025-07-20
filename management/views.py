from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from .models import Appointment, Doctor
from datetime import datetime, date, time


def home(request):
    return render(request, 'management/home.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'management/user_login.html')

def doctor_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user and hasattr(user, 'doctor'):
            login(request, user)
            return redirect('doctor_dashboard')
        messages.error(request, "Invalid credentials or not authorized as a doctor.")
    return render(request, 'management/doctor_login.html')

def admin_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user and user.is_superuser:
            login(request, user)
            return redirect('admin_dashboard')
        messages.error(request, "Invalid admin credentials.")
    return render(request, 'management/admin_login.html')

def user_register(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        if not name or not username or not password:
            messages.error(request, 'All fields are required.')
            return render(request, 'management/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'management/register.html')

        User.objects.create_user(username=username, password=password, first_name=name)
        messages.success(request, 'Account created successfully. Please log in.')
        return redirect('user_login')
    return render(request, 'management/register.html')

@login_required
def dashboard(request):
    if request.method == 'POST':
        if 'book_appointment' in request.POST:
            doctor_id = request.POST.get('doctor')
            appointment_date = request.POST.get('date')
            time_slot = request.POST.get('time_slot')

            try:
                doctor = Doctor.objects.get(id=doctor_id)
                appointment_date = datetime.strptime(appointment_date, "%Y-%m-%d").date()
                time_slot = datetime.strptime(time_slot, "%H:%M").time()

                if Appointment.objects.filter(doctor=doctor, date=appointment_date, time_slot=time_slot).exists():
                    messages.error(request, "This time slot is already booked.")
                else:
                    Appointment.objects.create(user=request.user, doctor=doctor, date=appointment_date, time_slot=time_slot)
                    messages.success(request, "Appointment booked successfully!")
            except Exception as e:
                messages.error(request, "Invalid data. Please try again.")

        elif 'cancel_appointment' in request.POST:
            appointment_id = request.POST.get('appointment_id')
            try:
                appointment = Appointment.objects.get(id=appointment_id, user=request.user)
                appointment.delete()
                messages.success(request, "Appointment canceled successfully.")
            except Appointment.DoesNotExist:
                messages.error(request, "Appointment not found.")

    doctors = Doctor.objects.all()
    appointments = Appointment.objects.filter(user=request.user)
    return render(request, 'management/dashboard.html', {'appointments': appointments, 'doctors': doctors})



@login_required
def fetch_time_slots(request):
    doctor_id = request.GET.get('doctor')
    appointment_date = request.GET.get('date')

    try:
        appointment_date = datetime.strptime(appointment_date, "%Y-%m-%d").date()
        if appointment_date < date.today():
            return JsonResponse({'error': 'You cannot select a past date.'}, status=400)

        doctor = Doctor.objects.get(id=doctor_id)

        all_time_slots = [time(hour, 0).strftime("%H:%M") for hour in range(9, 17)]

        booked_time_slots = Appointment.objects.filter(
            doctor=doctor, date=appointment_date
        ).values_list('time_slot', flat=True)
        booked_time_slots = [slot.strftime("%H:%M") for slot in booked_time_slots]

        current_time = datetime.now().time()
        if appointment_date == date.today():
            all_time_slots = [slot for slot in all_time_slots if time.fromisoformat(slot) > current_time]

        available_time_slots = [slot for slot in all_time_slots if slot not in booked_time_slots]

        return JsonResponse({'time_slots': available_time_slots})

    except Doctor.DoesNotExist:
        return JsonResponse({'error': 'Invalid doctor ID.'}, status=400)
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Invalid date format.'}, status=400)


@login_required
def doctor_dashboard(request):
    if not hasattr(request.user, 'doctor'):
        return redirect('user_login')

    if request.method == "POST":
        appointment_id = request.POST.get('appointment_id')

        if 'complete_appointment' in request.POST:
            appointment = Appointment.objects.get(id=appointment_id)
            appointment.completed = True
            appointment.save()
            messages.success(request, "Appointment marked as completed.")

        elif 'remove_appointment' in request.POST:
            appointment = Appointment.objects.get(id=appointment_id)
            appointment.delete()
            messages.success(request, "Appointment removed successfully.")

        elif 'cancel_appointment' in request.POST:
            appointment = Appointment.objects.get(id=appointment_id)
            appointment.delete()
            messages.success(request, "Appointment canceled successfully.")

        return redirect('doctor_dashboard')

    appointments = Appointment.objects.filter(doctor=request.user.doctor)
    return render(request, 'management/doctor_dashboard.html', {'appointments': appointments})


@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect('user_login')

    doctors = Doctor.objects.all()

    if request.method == 'POST':
        if 'add_doctor' in request.POST:
            username = request.POST['username'].strip()
            password = request.POST['password'].strip()
            first_name = request.POST['first_name'].strip()
            last_name = request.POST['last_name'].strip()
            specialization = request.POST['specialization'].strip()

            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists. Please choose a different one.")
                return redirect('admin_dashboard')

            if not username or not password or not first_name or not last_name or not specialization:
                messages.error(request, "All fields are required.")
                return redirect('admin_dashboard')

            try:
                user = User.objects.create_user(username=username, password=password, first_name=first_name, last_name=last_name)
                Doctor.objects.create(user=user, specialization=specialization)
                messages.success(request, "Doctor added successfully.")
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
                return redirect('admin_dashboard')

        elif 'delete_doctor' in request.POST:
            doctor_id = request.POST.get('doctor_id')
            try:
                doctor = Doctor.objects.get(id=doctor_id)
                doctor.user.delete()
                doctor.delete()
                messages.success(request, "Doctor deleted successfully.")
            except Doctor.DoesNotExist:
                messages.error(request, "Doctor not found.")

    return render(request, 'management/admin_dashboard.html', {'doctors': doctors})


def user_logout(request):
    logout(request)
    return redirect('user_login')