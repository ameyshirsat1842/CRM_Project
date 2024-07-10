from celery.utils.time import timezone
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from .forms import SignUpForm, AddRecordForm, AddTicketForm, UpdateRecordForm
from .models import Record, Notification, Ticket


def home(request):
    return render(request, 'home.html')


def leads(request):
    records = Record.objects.all()
    return render(request, 'leads.html', {'records': records})


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


def lead(request):
    user = request.user
    # Fetch records where the logged-in user is in the visible_to list or the assigned_to field
    records = Record.objects.filter(visible_to=user) | Record.objects.filter(assigned_to=user)
    return render(request, 'leads.html', {'records': records.distinct()})


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
        form = AddRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)  # Save the form data without committing to the database yet

            # Save the record instance first to get an id
            record.save()

            # Now handle the many-to-many field 'visible_to'
            visible_to_ids = request.POST.getlist('visible_to')
            if visible_to_ids:
                users = User.objects.filter(id__in=visible_to_ids)
                record.visible_to.set(users)

            messages.success(request, "Record added successfully!")
            return redirect('leads')  # Redirect to leads page after successful save
    else:
        form = AddRecordForm()

    users = User.objects.all()
    return render(request, 'add_record.html', {'form': form, 'users': users})


def update_record(request, pk):
    record = get_object_or_404(Record, pk=pk)
    if request.method == 'POST':
        form = UpdateRecordForm(request.POST, instance=record)
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

            return redirect('leads')
    else:
        form = UpdateRecordForm(instance=record)

    users = User.objects.all()
    return render(request, 'update_record.html', {'form': form, 'users': users})


def submit_lead(request):
    if request.method == "POST":
        form = AddRecordForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Lead submitted successfully!")
            return redirect('home')
        else:
            messages.error(request, "Error submitting lead. Please check your inputs.")
    else:
        form = AddRecordForm()
    return render(request, 'add_record.html', {'form': form})


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
