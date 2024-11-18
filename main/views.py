# main/views.py

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.db import models
from django.http import JsonResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .forms import LoginForm, RegistrationForm, UserProfileForm, VehicleForm, MaintenanceArticleForm, QuoteForm, \
    AppointmentForm, RepairRequestForm
from .models import Appointment, Vehicle, RepairRequest, Quote, MaintenanceArticle, User, Message


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            print(user)
            if user.role == 'Admin':
                return redirect('admin_dashboard')
            else:
                return redirect('user_dashboard')
    else:
        form = LoginForm()
    return render(request, 'main/login.html', {'form': form})


def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            role = form.cleaned_data['role']
            if role == 'Admin':
                group, created = Group.objects.get_or_create(name='Admin')
            else:
                group, created = Group.objects.get_or_create(name='User')
            user.groups.add(group)

            messages.success(request, 'Registration successful. Please log in.')
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'main/register.html', {'form': form})


def user_dashboard(request):
    usees = get_object_or_404(User, username="admin")
    usees = get_object_or_404(User, username="admin")
    return render(request, 'dashboard/user_dashboard.html', {"userad": usees})


@login_required
def profile_view(request):
    if request.method == 'POST':
        user_form = UserProfileForm(request.POST, instance=request.user)
        if user_form.is_valid():
            user_form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('profile')
    else:
        user_form = UserProfileForm(instance=request.user)
    return render(request, 'main/dashboard/profile.html', {'user_form': user_form})


@login_required
def appointments_view(request):
    user = request.user
    appointments = Appointment.objects.filter(user=user).order_by('appointment_date')

    if request.method == 'POST':
        appointment_id = request.POST.get('appointment_id')
        action = request.POST.get('action')

        try:
            appointment = Appointment.objects.get(id=appointment_id, user=user)
            if action == 'confirm':
                appointment.status = 'Confirmed'
                appointment.save()
                messages.success(request, "Appointment confirmed successfully!")
            elif action == 'cancel':
                appointment.status = 'Canceled'
                appointment.save()
                messages.success(request, "Appointment canceled successfully!")
            return redirect('appointments')

        except Appointment.DoesNotExist:
            messages.error(request, "Appointment not found.")
            return redirect('appointments')

    return render(request, 'main/dashboard/appointments.html', {'appointments': appointments})


@login_required
def vehicle_list(request):
    vehicles = Vehicle.objects.all()
    return render(request, 'vehicles/vehicle_list.html', {'vehicles': vehicles})


@login_required
def vehicle_create(request):
    if request.method == 'POST':
        form = VehicleForm(request.POST)
        if form.is_valid():
            vehicle = form.save(commit=False)
            vehicle.user = request.user
            if not vehicle.last_maintenance_date:
                vehicle.last_maintenance_date = timezone.now()
            vehicle.save()
            messages.success(request, "Vehicle created successfully!")
            return redirect('vehicle_list')
    else:
        form = VehicleForm()
    return render(request, 'vehicles/vehicle_form.html', {'form': form, 'action': 'Create'})


@login_required
def vehicle_update(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    if request.method == 'POST':
        form = VehicleForm(request.POST, instance=vehicle)
        if form.is_valid():
            form.save()
            messages.success(request, "Vehicle updated successfully!")
            return redirect('vehicle_list')
    else:
        form = VehicleForm(instance=vehicle)
    return render(request, 'vehicles/vehicle_form.html', {'form': form, 'action': 'Update'})


@login_required
def vehicle_delete(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    if request.method == 'POST':
        vehicle.delete()
        messages.success(request, "Vehicle deleted successfully!")
        return redirect('vehicle_list')
    return render(request, 'vehicles/vehicle_confirm_delete.html', {'vehicle': vehicle})


@login_required
def admin_dashboard(request):
    repair_requests = RepairRequest.objects.all()
    appointments = Appointment.objects.all()
    quotes = Quote.objects.all()
    vehicles = Vehicle.objects.all()
    articles = MaintenanceArticle.objects.all()
    users = User.objects.all()
    context = {
        'repair_requests': repair_requests,
        'appointments': appointments,
        'quotes': quotes,
        'vehicles': vehicles,
        'articles': articles,
        'users': users
    }
    return render(request, 'dashboard/admin_dashboard.html', context)


@login_required
def repair_request_detail(request, pk):
    repair_request = get_object_or_404(RepairRequest, pk=pk)
    return render(request, 'admin/repair_request_detail.html', {'repair_request': repair_request})


@login_required
def repair_request_update(request, pk):
    repair_request = get_object_or_404(RepairRequest, pk=pk)
    if request.method == 'POST':
        form = RepairRequestForm(request.POST, instance=repair_request)
        if form.is_valid():
            form.save()
            messages.success(request, "Repair request updated successfully.")
            return redirect('admin_dashboard')
    else:
        form = RepairRequestForm(instance=repair_request)
    return render(request, 'admin/repair_request_update.html', {'form': form})


@login_required
def appointment_detail(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    return render(request, 'admin/appointment_detail.html', {'appointment': appointment})


@login_required
def appointment_update(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, "Appointment updated successfully.")
            return redirect('admin_dashboard')
    else:
        form = AppointmentForm(instance=appointment)
    return render(request, 'admin/appointment_update.html', {'form': form})


@login_required
def quote_detail(request, pk):
    quote = get_object_or_404(Quote, pk=pk)
    return render(request, 'admin/quote_detail.html', {'quote': quote})


@login_required
def quote_update(request, pk):
    quote = get_object_or_404(Quote, pk=pk)
    if request.method == 'POST':
        form = QuoteForm(request.POST, instance=quote)
        if form.is_valid():
            form.save()
            messages.success(request, "Quote updated successfully.")
            return redirect('admin_dashboard')
    else:
        form = QuoteForm(instance=quote)
    return render(request, 'admin/quote_update.html', {'form': form})


@login_required
def vehicle_detail(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    return render(request, 'admin/vehicle_detail.html', {'vehicle': vehicle})


@login_required
def vehicle_update(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    if request.method == 'POST':
        form = VehicleForm(request.POST, instance=vehicle)
        if form.is_valid():
            form.save()
            messages.success(request, "Vehicle updated successfully.")
            return redirect('admin_dashboard')
    else:
        form = VehicleForm(instance=vehicle)
    return render(request, 'admin/vehicle_update.html', {'form': form})


@login_required
def article_detail(request, pk):
    article = get_object_or_404(MaintenanceArticle, pk=pk)
    return render(request, 'admin/article_detail.html', {'article': article})


@login_required
def article_update(request, pk):
    article = get_object_or_404(MaintenanceArticle, pk=pk)
    if request.method == 'POST':
        form = MaintenanceArticleForm(request.POST, instance=article)
        if form.is_valid():
            form.save()
            messages.success(request, "Article updated successfully.")
            return redirect('admin_dashboard')
    else:
        form = MaintenanceArticleForm(instance=article)
    return render(request, 'admin/article_update.html', {'form': form})


@login_required
def repair_request_add(request):
    if request.method == 'POST':
        form = RepairRequestForm(request.POST)
        if form.is_valid():
            repair_request = form.save(commit=False)
            repair_request.user = request.user  # Optionally assign the user
            repair_request.save()
            return redirect('admin_dashboard')  # Redirect after successful form submission
    else:
        form = RepairRequestForm()
    return render(request, 'admin/repair_request_add.html', {'form': form})


# Appointment Add
@login_required
def appointment_add(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.user = request.user  # Optionally assign the user
            appointment.save()
            return redirect('admin_dashboard')  # Redirect after successful form submission
    else:
        form = AppointmentForm()
    return render(request, 'admin/appointment_add.html', {'form': form})


# Quote Add
@login_required
def quote_add(request):
    if request.method == 'POST':
        form = QuoteForm(request.POST)
        if form.is_valid():
            quote = form.save(commit=False)
            quote.save()
            return redirect('admin_dashboard')  # Redirect after successful form submission
    else:
        form = QuoteForm()
    return render(request, 'admin/quote_add.html', {'form': form})


# Vehicle Add
@login_required
def vehicle_add(request):
    if request.method == 'POST':
        form = VehicleForm(request.POST)
        if form.is_valid():
            vehicle = form.save(commit=False)
            vehicle.save()
            return redirect('admin_dashboard')
    else:
        form = VehicleForm()
    return render(request, 'admin/vehicle_add.html', {'form': form})


# Article Add
@login_required
def article_add(request):
    if request.method == 'POST':
        form = MaintenanceArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.save()
            return redirect('admin_dashboard')  # Redirect after successful form submission
    else:
        form = MaintenanceArticleForm()
    return render(request, 'admin/article_add.html', {'form': form})


@login_required
def chat_view(request, user_id):
    try:
        receiver = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise Http404("User not found")

    # Fetch all messages between the current user and the receiver
    messages = Message.objects.filter(
        (models.Q(sender=request.user) & models.Q(receiver=receiver)) |
        (models.Q(sender=receiver) & models.Q(receiver=request.user))
    ).order_by('sent_at')

    # Send messages and receiver to template
    return render(request, 'chat.html', {
        'receiver': receiver,
        'messages': messages,
    })


@login_required
def send_message(request, user_id):
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            try:
                receiver = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return JsonResponse({'error': 'User not found'}, status=404)

            # Create a new message
            message = Message.objects.create(
                sender=request.user,
                receiver=receiver,
                content=content
            )

            # Return the message details as a JSON response
            return JsonResponse({
                'sender': message.sender.username,
                'content': message.content,
                'sent_at': message.sent_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        else:
            return JsonResponse({'error': 'No content provided'}, status=400)
    return JsonResponse({'error': 'Invalid method'}, status=405)


@login_required
def article_list(request):
    articles = MaintenanceArticle.objects.all()
    return render(request, 'main/articles_list.html', {'articles': articles})


@login_required
def article_detail_user(request, pk):
    article = get_object_or_404(MaintenanceArticle, pk=pk)
    return render(request, 'main/article_detail.html', {'article': article})


@login_required
def appointment_add_user(request):
    """
        View to handle the creation of a new appointment.
        """
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.user = request.user  # Assign the logged-in user to the appointment
            appointment.status = 'Pending'  # Set the default status to 'Pending'
            appointment.save()
            messages.success(request, "Your appointment has been added successfully!")
            return redirect('appointments')
        else:
            messages.error(request, "There was an error in your form. Please correct it and try again.")
    else:
        form = AppointmentForm()

    return render(request, 'main/dashboard/add-appointment.html', {'form': form})