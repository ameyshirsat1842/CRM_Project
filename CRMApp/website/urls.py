from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_user, name='register'),
    path('record/<int:pk>/', views.customer_record, name='record'),
    path('update_record/<int:pk>/', views.update_record, name='update_record'),
    path('delete/<int:pk>/', views.delete_record, name='delete_record'),
    path('leads/', views.leads, name='leads'),
    path('add/', views.add_record, name='add_record'),
    path('submit_lead/', views.submit_lead, name='submit_lead'),
    path('tickets/', views.tickets, name='tickets'),
    path('tickets/add/', views.add_ticket, name='add_ticket'),
    path('tickets/update/<int:pk>/', views.update_ticket, name='update_ticket'),
    path('notifications/', views.notifications, name='notifications'),

]
