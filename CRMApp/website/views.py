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
