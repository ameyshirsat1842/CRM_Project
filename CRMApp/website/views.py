from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from .forms import SignUpForm, AddRecordForm
from .models import Record, Notification


def home(request):
    records = Record.objects.all()
    return render(request, 'home.html', {'records': records})


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


def customer_record(request, pk):
    if request.user.is_authenticated:
        customer_rec = Record.objects.get(id=pk)
        return render(request, 'record.html', {'customer_record': customer_rec})
    else:
        messages.error(request, "You must be logged in to view the record")
        return redirect('home')


def delete_record(request, pk):
    if request.user.is_authenticated:
        delete_it = Record.objects.get(id=pk)
        delete_it.delete()
        messages.success(request, "Record deleted successfully")
        return redirect('home')
    else:
        messages.error(request, "You must be logged in to view the record")
        return redirect('home')


def add_record(request):
    form = AddRecordForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "You have successfully added a new lead!")
            return redirect('home')
        else:
            messages.error(request, "Error adding lead. Please check your inputs.")
    return render(request, 'add_record.html', {'form': form})


def update_record(request, pk):
    record = get_object_or_404(Record, pk=pk)
    form = AddRecordForm(request.POST or None, instance=record)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Lead details updated successfully!")
            return redirect('home')
        else:
            messages.error(request, "Error updating lead. Please check your inputs.")

    return render(request, 'update_record.html', {'form': form, 'record': record})


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
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
        return render(request, 'notifications.html', {'notifications': notifications})
    else:
        messages.error(request, "You must be logged in to view notifications")
        return redirect('home')
