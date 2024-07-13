from celery.utils.time import timezone
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from .forms import SignUpForm, AddRecordForm, AddTicketForm, UpdateRecordForm, MeetingRecordForm
from .models import Record, Notification, Ticket, MeetingRecord
from django.views.generic import ListView


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

        context = {'records': records}
        return render(request, 'leads.html', context)
    else:
        return redirect('login')


def customer_record(request, pk):
    if request.user.is_authenticated:
        customer_rec = get_object_or_404(Record, id=pk)
        return render(request, 'record.html', {'customer_record': customer_rec})
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
        form = AddRecordForm(request.POST, request.FILES)
        if form.is_valid():
            record = form.save(commit=False)  # Save the form data without committing to the database yet

            record.save()

            visible_to_ids = request.POST.getlist('visible_to')
            if visible_to_ids:
                users = User.objects.filter(id__in=visible_to_ids)
                record.visible_to.set(users)

            messages.success(request, "Record added successfully!")
            return redirect('leads')
    else:
        form = AddRecordForm()

    users = User.objects.all()
    return render(request, 'add_record.html', {'form': form, 'users': users})


def update_record(request, pk):
    record = get_object_or_404(Record, pk=pk)
    if request.method == 'POST':
        form = UpdateRecordForm(request.POST, request.FILES, instance=record)
        if form.is_valid():
            record = form.save(commit=False)

            assigned_to_id = request.POST.get('assigned_to')
            if assigned_to_id:
                record.assigned_to = User.objects.get(id=assigned_to_id)

            record.save()

            visible_to_ids = request.POST.getlist('visible_to')
            if visible_to_ids:
                users = User.objects.filter(id__in=visible_to_ids)
                record.visible_to.set(users)

            messages.success(request, "Record updated successfully!")
            return redirect('leads')
    else:
        form = UpdateRecordForm(instance=record)

    users = User.objects.all()
    return render(request, 'update_record.html', {'form': form, 'users': users})


def notifications(request):
    if request.user.is_authenticated:
        user_notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
        return render(request, 'notifications.html', {'notifications': user_notifications})
    else:
        messages.error(request, "You must be logged in to view notifications")
        return redirect('home')


def create_notification(sender, instance, **kwargs):
    if instance.follow_up_date and instance.follow_up_date == timezone.now().date():
        message = f"Follow up with {instance.client_name} from {instance.company} is due today."
        Notification.objects.create(user=instance.user, message=message)


def tickets(request):
    # Query all tickets
    ticket = Ticket.objects.all()

    # Pass tickets to the template for rendering
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


def meeting_records(request):
    records = MeetingRecord.objects.filter(created_by=request.user)
    return render(request, 'meeting_records.html', {'records': records})


def add_meeting_record(request):
    if request.method == 'POST':
        form = MeetingRecordForm(request.POST)
        if form.is_valid():
            meeting_record = form.save(commit=False)
            meeting_record.created_by = request.user
            meeting_record.save()
            messages.success(request, "Meeting record added successfully!")
            return redirect('meeting_records')
    else:
        form = MeetingRecordForm()
    return render(request, 'add_meeting_record.html', {'form': form})


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
        form = MeetingRecordForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            messages.success(request, "Meeting record updated successfully!")
            return redirect('meeting_records')
    else:
        form = MeetingRecordForm(instance=record)
    return render(request, 'update_meeting_record.html', {'form': form})


def delete_meeting_record(request, pk):
    record = get_object_or_404(MeetingRecord, pk=pk)
    if request.method == 'POST':
        record.delete()
        messages.success(request, "Meeting record deleted successfully!")
        return redirect('meeting_records')
    return render(request, 'delete_meeting_record.html', {'record': record})
