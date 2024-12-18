from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('', views.user_dashboard, name='user_dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('appointments/', views.appointments_view, name='appointments'),
    path('vehicles/', views.vehicle_list, name='vehicle_list'),
    path('vehicles/create', views.vehicle_create, name='vehicle_create'),
    path('vehicles/update/<int:pk>', views.vehicle_update, name='vehicle_update'),
    path('vehicles/delete/<int:pk>/', views.vehicle_delete, name='vehicle_delete'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),

    path('admin-repair-requests/', views.repair_requests, name='admin_repair_requests'),
    path('admin-appointments/', views.appointments, name='admin_appointments'),
    path('admin-quotes/', views.quotes, name='admin_quotes'),
    path('admin-vehicles/', views.vehicles, name='admin_vehicles'),
    path('admin-maintenance-articles/', views.maintenance_articles, name='admin_maintenance_articles'),
    # Repair Requests
    path('repair-request/<int:pk>/', views.repair_request_detail, name='repair_request_detail'),
    path('repair-request/update/<int:pk>/', views.repair_request_update, name='repair_request_update'),
    path('repair-request/add/', views.repair_request_add, name='repair_request_add'),  # Add repair request
    path('user-repair-request/add/', views.repair_request_add_user, name='repair_request_add_user'),  # Add repair request


    path('appointment/<int:pk>/', views.appointment_detail, name='appointment_detail'),
    path('appointment/update/<int:pk>/', views.appointment_update, name='appointment_update'),
    path('appointment/add/', views.appointment_add, name='appointment_add'),  # Add appointment

    path('quote/<int:pk>/', views.quote_detail, name='quote_detail'),
    path('quote/update/<int:pk>/', views.quote_update, name='quote_update'),
    path('quote/add/', views.quote_add, name='quote_add'),  # Add quote

    path('vehicle/<int:pk>/', views.vehicle_detail, name='vehicle_detail'),
    path('vehicle/update/<int:pk>/', views.vehicle_update, name='vehicle_update'),
    path('vehicle/add/', views.vehicle_add, name='vehicle_add'),  # Add vehicle

    path('article/<int:pk>/', views.article_detail, name='article_detail'),
    path('article/update/<int:pk>/', views.article_update, name='article_update'),
    path('article/add/', views.article_add, name='article_add'),
    path('chat/<int:user_id>/', views.chat_view, name='chat_view'),
    path('send_message/<int:user_id>/', views.send_message, name='send_message'),

    path('articles', views.article_list, name='article_list'),
    path('article/deatials/<int:pk>/', views.article_detail_user, name='article_detail_user'),
    path('add-appointment/', views.appointment_add_user, name='add_appointment_user'),


# gd3
    path('repair-request/edit/', views.edit_repair_request, name='repair_request_edit'),
    path('repair-request/delete/', views.delete_repair_request, name='repair_request_delete'),


    path('vehicles/edit/<int:vehicle_id>/', views.edit_vehicle, name='edit_vehicle'),
    path('vehicles/delete/<int:vehicle_id>/', views.delete_vehicle, name='delete_vehicle'),

    path('appointments/edit/<int:appointment_id>/', views.edit_appointment, name='edit_appointment'),
    path('appointments/delete/<int:appointment_id>/', views.delete_appointment, name='delete_appointment'),

    path('quotes/edit/<int:quote_id>/', views.edit_quote, name='edit_quote'),
    path('quotes/delete/<int:quote_id>/', views.delete_quote, name='delete_quote'),

    path('article/<int:pk>/', views.article_detail, name='article_detail'),
    path('article/edit/<int:pk>/', views.article_edit, name='article_edit'),
    path('article/delete/<int:pk>/', views.article_delete, name='article_delete'),

    path('repair-quotes/edit/<int:pk>/', views.quote_edit, name='quote_edit'),
    path('repair-quotes/delete/<int:pk>/', views.quote_delete, name='quote_delete'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)