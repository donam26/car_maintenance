# main/views.py

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, User
from django.db import models
from django.http import JsonResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db.models import Count, Sum

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
    vehicles = Vehicle.objects.filter(user=user)

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

    return render(request, 'main/dashboard/appointments.html', {'appointments': appointments,'vehicles': vehicles,})


@login_required
def vehicle_list(request):
    if request.method == 'POST':
        make = request.POST.get('make')
        model = request.POST.get('model')
        year = request.POST.get('year')
        vin = request.POST.get('vin')
        color = request.POST.get('color', '')  # Mặc định là chuỗi rỗng nếu không nhập
        license_plate = request.POST.get('license_plate', '')  # Mặc định là chuỗi rỗng nếu không nhập

        if not make or not model or not year or not vin:
            messages.error(request, "All fields marked as required must be filled!")
        else:
            # Tạo Vehicle mới
            Vehicle.objects.create(
                make=make,
                model=model,
                year=year,
                vin=vin,
                color=color,
                license_plate=license_plate,
                user_id=request.user.id  # Liên kết với user hiện tại
            )
            messages.success(request, "Vehicle added successfully!")

        return redirect('vehicle_list')

    # Lấy danh sách các Vehicle của user hiện tại
    vehicles = Vehicle.objects.filter(user_id=request.user.id)
    return render(request, 'main/dashboard/vehicles.html', {'vehicles': vehicles})

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
    from datetime import datetime
    now = datetime.now()
    monthly_repairs = RepairRequest.objects.filter(
        created_at__year=now.year, created_at__month=now.month
    )

    # Aggregate data for analysis
    report_data = monthly_repairs.values('user__username').annotate(
        total_repairs=Count('id'),
        total_cost=Sum('cost'),  # Assuming there is a 'cost' field in RepairRequest
    ).order_by('-total_repairs')

    return render(request, 'dashboard/admin_dashboard.html', {'report_data': report_data, 'month': now.strftime('%B %Y')})


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


def repair_request_add_user(request):
    if request.method == 'POST':
        vehicle_id = request.POST.get('vehicle_id')
        description = request.POST.get('description')
        try:
            vehicle = Vehicle.objects.get(id=vehicle_id, user=request.user)
            repair_request = RepairRequest.objects.create(
                vehicle=vehicle,
                description=description,
                user=request.user
            )
            messages.success(request, "Repair request added successfully,Please wait for us to schedule an appointment!")
        except Vehicle.DoesNotExist:
            messages.error(request, "Invalid vehicle.")
        return redirect('appointments') 
    return redirect('appointments') 

@login_required
def repair_request_add(request):
    if request.method == 'POST':
        repair_request_id = request.POST.get('repair_request_id')
        repair_request = get_object_or_404(RepairRequest, id=repair_request_id)
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.repair_request = repair_request
            appointment.user = request.user
            appointment.status = 'Pending'
            appointment.save()
            messages.success(request, "Appointment created successfully!")
            return redirect('repair_requests')  # Redirect to repair requests page
        else:
            messages.error(request, "Failed to create appointment. Please correct the errors.")
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
            return redirect('admin_vehicles')
    else:
        form = VehicleForm()
    return render(request, 'admin/vehicle_add.html', {'form': form})


# Article Add
@login_required
def article_add(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        category = request.POST.get('category')
        image = request.FILES.get('image')

        # Lưu article mới với hình ảnh
        article = MaintenanceArticle(title=title, content=content, image=image)
        article.save()
        return redirect('admin_maintenance_articles')  # Redirect after successful form submission
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
    if request.method == 'POST':
        repair_request_id = request.POST.get('repair_request_id')  # Lấy ID RepairRequest từ POST
        if not repair_request_id:
            messages.error(request, "Repair Request ID is missing.")
            return redirect('admin_appointments')

        # Lấy đối tượng RepairRequest
        repair_request = get_object_or_404(RepairRequest, id=repair_request_id)

        # Khởi tạo form với dữ liệu POST
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.user = repair_request.user  # Gán user của khách hàng liên quan đến RepairRequest
            appointment.repair_request = repair_request  # Gán đối tượng RepairRequest
            appointment.status = "Pending"  # Gán đối tượng RepairRequest
            appointment.cost = form.cleaned_data['cost']  # Lấy cost từ dữ liệu form nhập vào
            appointment.save()  # Lưu đối tượng Appointment

            repair_request.delete()
            return redirect('admin_appointments')
        else:
            # In lỗi form để kiểm tra
            print(f"Form Errors: {form.errors}")
            messages.error(request, "There was an error in your form. Please correct it and try again.")
    return redirect('admin_appointments')

def repair_requests(request):
    repair_requests = RepairRequest.objects.all()  # Fetch all repair requests
    return render(request, 'dashboard/repair_requests.html', {'repair_requests': repair_requests})

def appointments(request):
    appointments = Appointment.objects.select_related('repair_request', 'user').all()  # Query tất cả các cuộc hẹn
    return render(request, 'dashboard/appointments.html', {'appointments': appointments})

def quotes(request): 
    # Lấy tất cả các quotes kèm theo thông tin từ bảng RepairRequest qua quan hệ ForeignKey
    quotes = Quote.objects.select_related('repair_request').all()
    
    # Lấy tất cả các repair requests để hiển thị trong form
    repair_requests = RepairRequest.objects.all()

    if request.method == 'POST':
        # Sử dụng QuoteForm để tạo mới
        form = QuoteForm(request.POST)

        if form.is_valid():
            # Lưu thông tin Quote
            quote = form.save(commit=False)

            # Kiểm tra và gán RepairRequest cho Quote
            repair_request_id = request.POST.get('repair_request_id')
            if repair_request_id:
                repair_request = get_object_or_404(RepairRequest, id=repair_request_id)
                quote.repair_request = repair_request
                quote.save()  # Lưu vào database
                messages.success(request, "Repair Quote added successfully!")
                return redirect('admin_quotes')  # Redirect sau khi thành công
            else:
                messages.error(request, "Repair Request ID is missing.")
        else:
            messages.error(request, f"Error: {form.errors}")

    # Trả về trang danh sách quotes
    form = QuoteForm()
    return render(request, 'dashboard/quotes.html', {
        'quotes': quotes,  # Truyền danh sách quotes
        'repair_requests': repair_requests,  # Truyền danh sách repair requests
        'form': form,  # Form để thêm mới
    })
def vehicles(request):
    vehicle_list = Vehicle.objects.all()
    return render(request, 'dashboard/vehicles.html', {'vehicle_list': vehicle_list})

def maintenance_articles(request):
    # Fetch maintenance articles data from the database
    articles = MaintenanceArticle.objects.all()
    return render(request, 'dashboard/maintenance_articles.html', {'articles': articles})

def edit_repair_request(request):
    if request.method == 'POST':
        request_id = request.POST.get('id')
        vehicle = request.POST.get('vehicle')
        status = request.POST.get('status')
        repair_request = get_object_or_404(RepairRequest, id=request_id)
        repair_request.vehicle.make = vehicle
        repair_request.status = status
        repair_request.save()
        return redirect('admin_repair_requests')

def delete_repair_request(request):
    if request.method == 'POST':
        request_id = request.POST.get('id')
        repair_request = get_object_or_404(RepairRequest, id=request_id)
        repair_request.delete()
        return redirect('admin_repair_requests')

def edit_vehicle(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)  # Fetch the vehicle object by ID
    
    if request.method == 'POST':
        vehicle.make = request.POST.get('make')
        vehicle.model = request.POST.get('model')
        vehicle.year = request.POST.get('year')
        vehicle.vin = request.POST.get('vin')
        vehicle.color = request.POST.get('color')
        vehicle.vin = request.POST.get('vin')  
        vehicle.license_plate = request.POST.get('license_plate')
        vehicle.last_maintenance = request.POST.get('last_maintenance')
        vehicle.color = request.POST.get('color')  # Save the color field
        vehicle.save()
        
        return redirect('vehicles')  # Redirect to the vehicles list after saving changes

    return render(request, 'dashboard/edit_vehicle.html', {'vehicle': vehicle})


# View for deleting vehicle
def delete_vehicle(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)  # Fetch the vehicle object by ID
    vehicle.delete()  # Delete the vehicle
    return redirect('vehicles') 


def edit_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    if request.method == 'POST':
        appointment_date = request.POST.get('appointment_date')
        status = request.POST.get('status')
        # Update the fields
        appointment.appointment_date = appointment_date
        appointment.status = status
        appointment.save()
        return redirect('appointments')  # Redirect to the appointments list

    # Render the edit form with current appointment data
    return render(request, 'dashboard/edit_appointment.html', {'appointment': appointment})

# View for deleting an appointment


def delete_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    if request.method == 'POST':
        appointment.delete()
        return redirect('admin_appointments')

def edit_quote(request, quote_id):
    quote = get_object_or_404(Quote, id=quote_id)
    if request.method == 'POST':
        quote.price = request.POST.get('price')
        quote.details = request.POST.get('details')
        quote.sent_to_user = request.POST.get('sent_to_user') == 'on'
        quote.save()
        return redirect('quotes')
    return render(request, 'dashboard/edit_quote.html', {'quote': quote})

def delete_quote(request, quote_id):
    quote = get_object_or_404(Quote, id=quote_id)
    if request.method == 'POST':
        quote.delete()
        return redirect('quotes')


def article_detail(request, pk):
    article = get_object_or_404(MaintenanceArticle, pk=pk)
    return render(request, 'dashboard/article_detail.html', {'article': article})

def article_edit(request, pk):
    # Lấy bài viết cần chỉnh sửa
    article = get_object_or_404(MaintenanceArticle, pk=pk)
    
    if request.method == 'POST':
        # Cập nhật các trường còn lại
        article.title = request.POST.get('title')
        article.content = request.POST.get('content')
        article.category = request.POST.get('category')
        
        # Kiểm tra xem có hình ảnh mới được upload không
        if 'image' in request.FILES:
            article.image = request.FILES['image']  # Cập nhật hình ảnh nếu có

        # Lưu bài viết sau khi chỉnh sửa
        article.save()
        
        # Chuyển hướng đến trang danh sách bài viết
        return redirect('admin_maintenance_articles')
    
    return render(request, 'dashboard/article_edit.html', {'article': article})

def article_delete(request, pk):
    article = get_object_or_404(MaintenanceArticle, pk=pk)
    if request.method == 'POST':
        article.delete()
        return redirect('admin_maintenance_articles')
    return render(request, 'dashboard/article_confirm_delete.html', {'article': article})


def quote_edit(request, pk):
    quote = get_object_or_404(Quote, pk=pk)

    if request.method == 'POST':
        # Lấy giá trị từ POST
        repair_request_id = request.POST.get('repair_request')  # Sử dụng đúng tên trường trong form
        price = request.POST.get('price')
        details = request.POST.get('details')

        # Kiểm tra và cập nhật repair_request
        if repair_request_id:
            repair_request = get_object_or_404(RepairRequest, pk=repair_request_id)
            quote.repair_request = repair_request

        # Cập nhật các trường khác
        quote.price = price
        quote.details = details
        quote.save()

        messages.success(request, "Repair Quote updated successfully!")
        return redirect('admin_quotes')

    # Nếu không phải POST, hiển thị lại trang
    form = QuoteForm(instance=quote)
    return render(request, 'dashboard/edit_quote.html', {'form': form, 'quote': quote})

# View to delete a Repair Quote
def quote_delete(request, pk):
    quote = get_object_or_404(Quote, pk=pk)
    if request.method == 'POST':
        quote.delete()
        messages.success(request, "Repair Quote deleted successfully!")
    return redirect('admin_quotes')