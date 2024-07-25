from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from .forms import SignUpForm, AddRecordForm, AddTicketForm, UpdateRecordForm, AddMeetingRecordForm, PotentialLeadForm
from .models import Record, Notification, Ticket, MeetingRecord, PotentialLead
from django.views.generic import ListView
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import pandas as pd
import pytz
from django.core.files.storage import FileSystemStorage
from io import BytesIO
from django.http import HttpResponse, HttpResponseBadRequest


def home(request):
    return render(request, 'home.html')


def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "You are logged in")
            return redirect('home')
        else:
            messages.error(request, "Invalid User")
            return redirect('login')
    else:
        return render(request, 'login.html')


def logout_user(request):
    logout(request)
    messages.success(request, "You have been logged out")
    return redirect('home')


def register_user(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "You have successfully registered!")
                return redirect('home')
            else:
                messages.error(request, "Registration successful but login failed. Please log in manually.")
                return redirect('login')
        else:
            messages.error(request, "There was an error with your registration. Please try again.")
    else:
        form = SignUpForm()

    return render(request, 'register.html', {'form': form})


def leads_view(request):
    if request.user.is_authenticated:
        search_query = request.GET.get('search', '')
        filter_option = request.GET.get('filter', '')

        # Apply search query
        if search_query:
            records = Record.objects.filter(
                Q(company__icontains=search_query) |
                Q(client_name__icontains=search_query) |
                Q(dept_name__icontains=search_query) |
                Q(phone__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(city__icontains=search_query) |
                Q(assigned_to__username__icontains=search_query) |
                Q(comments__icontains=search_query) |
                Q(remarks__icontains=search_query)
            )
        else:
            records = Record.objects.all()

        # Apply filter if specified
        if filter_option == 'assigned_to_me':
            records = records.filter(assigned_to=request.user)

        context = {'records': records}
        return render(request, 'leads.html', context)
    else:
        return redirect('login')


def customer_record(request, pk):
    if request.user.is_authenticated:
        customer_rec = get_object_or_404(Record, id=pk)
        meeting_records = MeetingRecord.objects.filter(record=customer_rec)
        return render(request, 'record.html', {'customer_record': customer_rec, 'meeting_records': meeting_records})

    else:
        messages.error(request, "You must be logged in to view the record")
        return redirect('home')


def delete_record(request, pk, record=None):
    if request.method == 'POST':
        record = get_object_or_404(Record, pk=pk)
        record.delete()
        messages.success(request, "Record deleted successfully")
        return redirect('leads')
    return render(request, 'delete_record.html', {'record': record})


def add_record(request):
    if request.method == 'POST':
        form = AddRecordForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            record = form.save(commit=False)
            record.created_by = request.user
            record.save()

            visible_to_ids = request.POST.getlist('visible_to')
            if visible_to_ids:
                users = User.objects.filter(id__in=visible_to_ids)
                record.visible_to.set(users)
                for user in users:
                    message = f"New record added by {request.user.username}: {record.company}"
                    send_notification_to_user(user, message)

            messages.success(request, "Record added successfully!")
            return redirect('leads')
        else:
            print(form.errors)
            messages.error(request, "There was an error with the form. Please check the details and try again.")
    else:
        form = AddRecordForm(user=request.user)

    users = User.objects.all()
    return render(request, 'add_record.html', {'form': form, 'users': users})


def update_record(request, pk):
    record = get_object_or_404(Record, pk=pk)
    if request.method == 'POST':
        form = UpdateRecordForm(request.POST, request.FILES, instance=record)
        if form.is_valid():
            updated_record = form.save(commit=False)
            updated_record.last_modified_by = request.user  # Save the user who modified the record
            form.save()
            messages.success(request, "Record updated successfully!")
            return redirect('leads')
    else:
        form = UpdateRecordForm(instance=record)

    users = User.objects.all()
    return render(request, 'update_record.html', {'form': form, 'record': record, 'users': users})


def notifications_view(request):
    if request.user.is_authenticated:
        notifications = Notification.objects.unread_for_user(request.user)
    else:
        notifications = []

    return render(request, 'notifications.html', {'notifications': notifications})


def mark_notification_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.mark_as_read()
    return redirect('notifications')


def tickets(request):
    # Query all tickets
    ticket = Ticket.objects.all()

    return render(request, 'tickets.html', {'tickets': ticket})


def add_ticket(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            form = AddTicketForm(request.POST)
            if form.is_valid():
                ticket = form.save(commit=False)
                ticket.created_by = request.user
                ticket.save()
                messages.success(request, "Ticket added successfully!")
                return redirect('tickets')
            else:
                # Debug: Print form errors to console
                print(form.errors)
                messages.error(request, "Error adding ticket. Please check your inputs.")
        else:
            form = AddTicketForm()
        return render(request, 'add_ticket.html', {'form': form})
    else:
        messages.error(request, "You must be logged in to add a ticket.")
        return redirect('login')


def update_ticket(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    if request.user.is_authenticated:
        if request.method == "POST":
            form = AddTicketForm(request.POST, instance=ticket)
            if form.is_valid():
                form.save()
                messages.success(request, "Ticket updated successfully!")
                return redirect('tickets')
            else:
                messages.error(request, "Error updating ticket. Please check your inputs.")
        else:
            form = AddTicketForm(instance=ticket)
        return render(request, 'update_ticket.html', {'form': form})
    else:
        messages.error(request, "You must be logged in to update a ticket.")
        return redirect('login')


def add_meeting_record(request, pk):
    record = get_object_or_404(Record, pk=pk)
    if request.method == 'POST':
        form = AddMeetingRecordForm(request.POST)
        if form.is_valid():
            meeting_record = form.save(commit=False)
            meeting_record.record = record
            meeting_record.created_by = request.user
            meeting_record.save()
            messages.success(request, "Meeting record added successfully!")
            return redirect('record', pk=record.pk)
    else:
        form = AddMeetingRecordForm()
    return render(request, 'add_meeting_record.html', {'form': form, 'record': record})


def meeting_records(request, pk):
    record = get_object_or_404(Record, pk=pk)
    records = record.meeting_records.all()
    return render(request, 'meeting_records.html', {'records': records, 'record': record})


class MeetingRecordListView(ListView):
    model = MeetingRecord
    template_name = 'meeting_records.html'
    context_object_name = 'records'
    paginate_by = 10  # Adjust as needed

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(meeting_partner__icontains=query) |
                Q(products_discussed_partner__icontains=query) |
                Q(products_discussed_company__icontains=query) |
                Q(conclusion__icontains=query) |
                Q(follow_up_date__icontains=query)
            )
        return queryset


def update_meeting_record(request, pk):
    record = get_object_or_404(MeetingRecord, pk=pk)
    if request.method == 'POST':
        form = AddMeetingRecordForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            messages.success(request, "Meeting record updated successfully!")
            return redirect('meeting_records')
    else:
        form = AddMeetingRecordForm(instance=record)
    return render(request, 'update_meeting_record.html', {'form': form})


def delete_meeting_record(request, pk):
    record = get_object_or_404(MeetingRecord, pk=pk)
    if request.method == 'POST':
        record.delete()
        messages.success(request, "Meeting record deleted successfully!")
        return redirect('meeting_records')
    return render(request, 'delete_meeting_record.html', {'record': record})


def leads_by_classification(request, classification):
    if classification == 'all':
        records = Record.objects.all()
    else:
        records = Record.objects.filter(classification=classification)

    context = {
        'user': request.user,
        'records': records,
    }
    return render(request, 'leads.html', context)


def add_potential_lead(request):
    if request.method == 'POST':
        form = PotentialLeadForm(request.POST)
        if form.is_valid():
            potential_lead = form.save(commit=False)
            potential_lead.created_by = request.user
            potential_lead.save()
            messages.success(request, "Potential lead added successfully!")
            return redirect('potential_leads')
    else:
        form = PotentialLeadForm()
    return render(request, 'add_potential_lead.html', {'form': form})


def potential_leads(request):
    leads = PotentialLead.objects.filter(created_by=request.user)
    return render(request, 'potential_leads.html', {'leads': leads})


def move_to_main_leads(request, lead_id):
    lead = PotentialLead.objects.get(id=lead_id)
    # Add logic to move lead to main leads
    main_lead = Record(
        company=lead.company,
        client_name=lead.client_name,
        phone=lead.phone,
        email=lead.email,
        comments=lead.comments,
        created_by=lead.created_by
    )
    main_lead.save()
    lead.delete()
    messages.success(request, "Lead moved to main leads successfully!")
    return redirect('leads')


def assign_lead(request, pk):
    lead = get_object_or_404(Record, pk=pk)
    if request.method == 'POST':
        lead.assigned_to = request.user
        lead.save()

        message = f"Lead assigned to you: {lead.company}"
        send_notification_to_user(request.user, message)

        messages.success(request, "Lead assigned successfully!")
        return redirect('leads')


def send_notification_to_user(user, message):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        user.username,
        {
            'type': 'send_notification',
            'notification': message
        }
    )


def export_record_to_excel(request, record_id):
    try:
        # Fetch the record by ID
        record = Record.objects.get(pk=record_id)

        # Convert timezone-aware datetime to timezone-naive
        if record.created_at.tzinfo is not None:
            created_at = record.created_at.astimezone(pytz.utc).replace(tzinfo=None)
        else:
            created_at = record.created_at

        if record.follow_up_date:
            follow_up_date = record.follow_up_date
        else:
            follow_up_date = None

        # Convert the record to a DataFrame
        data = {
            'ID': [record.id],
            'Company': [record.company],
            'Client Name': [record.client_name],
            'Department': [record.dept_name],
            'Phone': [record.phone],
            'Email': [record.email],
            'City': [record.city],
            'Address': [record.address],
            'Follow-Up Date': [follow_up_date],
            'Comments': [record.comments],
            'Remarks': [record.remarks],
            'Attachments': [record.attachments.name if record.attachments else 'No attachments'],
            'Assigned To': [record.assigned_to.username if record.assigned_to else 'N/A'],
            'Created By': [record.created_by.username],
            'Social Media Details': [record.social_media_details],
            'Classification': [record.classification],
            'Lead Source': [record.lead_source],
            'Created At': [created_at],
        }
        df = pd.DataFrame(data)

        # Create a BytesIO buffer
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)

        # Set the buffer position to the beginning
        buffer.seek(0)

        # Create the HttpResponse object
        response = HttpResponse(buffer,
                                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename=record_{record_id}.xlsx'

        return response
    except Record.DoesNotExist:
        return HttpResponse("Record not found.", status=404)


def import_records_from_excel(request):
    if request.method == 'POST' and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file']
        fs = FileSystemStorage()
        filename = fs.save(excel_file.name, excel_file)
        file_path = fs.path(filename)

        try:
            df = pd.read_excel(file_path)
            for _, row in df.iterrows():
                Record.objects.create(
                    created_at=row.get('created_at', None),
                    company=row.get('company', ''),
                    client_name=row.get('client_name', ''),
                    dept_name=row.get('dept_name', ''),
                    phone=row.get('phone', ''),
                    email=row.get('email', ''),
                    city=row.get('city', ''),
                    address=row.get('address', ''),
                    follow_up_date=row.get('follow_up_date', None),
                    comments=row.get('comments', ''),
                    remarks=row.get('remarks', ''),
                    attachments=row.get('attachments', ''),
                    assigned_to=User.objects.get(id=row.get('assigned_to_id')) if row.get('assigned_to_id') else None,
                    created_by=User.objects.get(id=row.get('created_by_id')) if row.get('created_by_id') else None,
                    social_media_details=row.get('social_media_details', ''),
                    classification=row.get('classification', ''),
                    lead_source=row.get('lead_source', ''),
                    last_modified_by=User.objects.get(id=row.get('last_modified_by_id')) if row.get('last_modified_by_id') else None
                )
            return redirect('leads')

        except Exception as e:
            return HttpResponseBadRequest(f"Error processing file: {e}")

    return render(request, 'import_leads.html')

