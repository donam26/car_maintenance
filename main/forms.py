# main/forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import User, Vehicle, RepairRequest, Appointment, Message, Notification, ServiceKnowledge, Quote, \
    MaintenanceArticle


class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    class Meta:
        model = User


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'role']


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['make', 'model', 'year', 'license_plate', 'vin', 'user']
        widgets = {
            'last_maintenance_date': forms.DateInput(attrs={'type': 'date'}),
        }


class RepairRequestForm(forms.ModelForm):
    class Meta:
        model = RepairRequest
        fields = ['user', 'vehicle', 'description', 'status', 'cost']
        widgets = {
            'status': forms.Select(choices=RepairRequest.STATUS_CHOICES),
        }


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['cost', 'appointment_date']
        widgets = {
            'appointment_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'status': forms.Select(choices=Appointment.STATUS_CHOICES),
        }


class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ['user', 'content', 'is_read']


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['sender', 'receiver', 'content']


class ServiceKnowledgeForm(forms.ModelForm):
    class Meta:
        model = ServiceKnowledge
        fields = ['title', 'content']


class QuoteForm(forms.ModelForm):
    class Meta:
        model = Quote
        fields = [ 'price', 'details']
        widgets = {
            'price': forms.NumberInput(attrs={'step': '0.01'}),
        }


class MaintenanceArticleForm(forms.ModelForm):
    class Meta:
        model = MaintenanceArticle
        fields = ['title', 'content', 'category', 'image']  # Thêm trường 'image' vào fields
