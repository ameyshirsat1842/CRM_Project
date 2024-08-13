from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import MeetingRecordListView, update_meeting_record, delete_meeting_record, import_records_from_excel, \
    settings_view, update_user_info

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_user, name='register'),
    path('record/<int:pk>/', views.customer_record, name='record'),
    path('update_record/<int:pk>/', views.update_record, name='update_record'),
    path('delete/<int:pk>/', views.delete_record, name='delete_record'),
    path('leads/', views.leads_view, name='leads'),
    path('add/', views.add_record, name='add_record'),
    path('add_meeting_record/<int:pk>/', views.add_meeting_record, name='add_meeting_record'),
    path('meeting-records/', MeetingRecordListView.as_view(), name='meeting_records'),
    path('tickets/', views.tickets, name='tickets'),
    path('tickets/add/', views.add_ticket, name='add_ticket'),
    path('tickets/update/<int:pk>/', views.update_ticket, name='update_ticket'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/mark-as-read/<int:notification_id>/', views.mark_notification_as_read,
         name='mark_notification_as_read'),
    path('notification/<int:pk>/', views.notification_detail, name='notification_detail'),
    path('meeting-records/update/<int:pk>/', update_meeting_record, name='update_meeting_record'),
    path('meeting-records/delete/<int:pk>/', delete_meeting_record, name='delete_meeting_record'),
    path('potential-leads/', views.potential_leads, name='potential_leads'),
    path('add-potential-lead/', views.add_potential_lead, name='add_potential_lead'),
    path('move-to-main-leads/<int:lead_id>/', views.move_to_main_leads, name='move_to_main_leads'),
    path('export_record/<int:record_id>/', views.export_record_to_excel, name='export_record'),
    path('import-leads/', import_records_from_excel, name='import_leads'),
    path('export-leads/', views.export_leads, name='export_leads'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('settings/', settings_view, name='settings'),
    path('update-info/', update_user_info, name='update_user_info'),

]
