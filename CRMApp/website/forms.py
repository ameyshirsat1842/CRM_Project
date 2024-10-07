from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Record, Ticket, MeetingRecord, PotentialLead, Customer
from .models import Profile


class SignUpForm(UserCreationForm):
    email = forms.EmailField(label="",
                             widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}))
    first_name = forms.CharField(label="", max_length=100,
                                 widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(label="", max_length=100,
                                widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    phone_number = forms.CharField(label="", max_length=15, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Phone Number'}), required=False)
    department = forms.CharField(label="", max_length=100,
                                 widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Department'}),
                                 required=False)

    class Meta:
        model = User
        fields = (
            'username', 'first_name', 'last_name', 'email', 'password1', 'password2')  # Exclude non-User model fields

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['username'].widget.attrs['placeholder'] = 'User Name'
        self.fields['username'].label = ''
        self.fields['username'].help_text = (
            '<span class="form-text text-muted"><small>Required. 150 characters or fewer. '
            'Letters, digits and @/./+/-/_ only.</small></span>')

        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['placeholder'] = 'Password'
        self.fields['password1'].label = ''
        self.fields['password1'].help_text = (
            '<ul class="form-text text-muted small"><li>Your password can\'t be too similar '
            'to your other personal information.</li><li>Your password must contain at '
            'least 8 characters.</li><li>Your password can\'t be a commonly used '
            'password.</li><li>Your password can\'t be entirely numeric.</li></ul>')

        self.fields['password2'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'
        self.fields['password2'].label = ''
        self.fields['password2'].help_text = (
            '<span class="form-text text-muted"><small>Enter the same password as before, '
            'for verification.</small></span>')

    def save(self, commit=True):
        user = super(SignUpForm, self).save(commit=False)
        if commit:
            user.save()
            Profile.objects.create(
                user=user,
                phone_number=self.cleaned_data.get('phone_number', ''),
                department=self.cleaned_data.get('department', '')
            )
        return user


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']


class ProfileUpdateForm(forms.ModelForm):
    phone_number = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    department = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False
    )

    class Meta:
        model = Profile
        fields = ['phone_number', 'department']


class AddRecordForm(forms.ModelForm):
    company = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Company", "class": "form-control"}),
        label="Company"
    )
    client_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Client Name", "class": "form-control"}),
        label="Client Name"
    )
    dept_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Department Name", "class": "form-control"}),
        label="Department Name"
    )
    phone = forms.CharField(
        required=True,
        max_length=10,
        widget=forms.TextInput(attrs={"placeholder": "Phone", "class": "form-control"}),
        label="Phone"
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={"placeholder": "Email", "class": "form-control"}),
        label="Email"
    )
    city = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "City", "class": "form-control"}),
        label="City"
    )
    address = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Address", "class": "form-control"}),
        label="Address"
    )
    assigned_to = forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Assigned To"
    )
    follow_up_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', "class": "form-control"}),
        required=False,
        label='Follow-Up Date & Time'
    )
    comments = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Comments", "class": "form-control"}),
        label="Comments"
    )
    remarks = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Remarks", "class": "form-control"}),
        label="Meeting Type"
    )
    social_media_details = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={'rows': 3, 'cols': 40, 'placeholder': 'Social Media Details', 'class': 'form-control'}),
        label='Social Media Details'
    )
    classification = forms.ChoiceField(
        choices=Record.CLASSIFICATION_CHOICES,
        required=True,
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Classification"
    )
    lead_source = forms.ChoiceField(
        choices=Record.LEAD_SOURCE_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Lead Source"
    )
    priority = forms.ChoiceField(
        choices=Record.PRIORITY_CHOICES,
        required=True,
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Priority"
    )
    value = forms.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={"placeholder": "Value", "class": "form-control"}),
        label="Value"
    )
    attachment = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={"class": "form-control"}),
        label="Attachment"
    )

    class Meta:
        model = Record
        fields = ['company', 'client_name', 'dept_name', 'phone', 'email', 'city', 'address', 'classification',
                  'assigned_to', 'visible_to', 'follow_up_date', 'comments', 'remarks', 'social_media_details',
                  'lead_source', 'value', 'attachment']
        widgets = {
            'created_by': forms.HiddenInput(),
            'social_media_details': forms.Textarea(attrs={'rows': 3, 'cols': 40}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['assigned_to'].queryset = User.objects.all()
            self.fields['visible_to'].queryset = User.objects.exclude(username=self.user.username)
            self.initial['assigned_to'] = self.user

    def clean(self):
        cleaned_data = super().clean()
        assigned_to = cleaned_data.get('assigned_to')
        visible_to = cleaned_data.get('visible_to', User.objects.none())  # Ensure visible_to is a QuerySet

        # Check for duplicates based on phone and email
        phone = cleaned_data.get('phone')
        email = cleaned_data.get('email')

        if Record.objects.filter(phone=phone, email=email).exists():
            raise forms.ValidationError("A record with this phone number and email already exists.")

        if assigned_to == self.user:
            visible_to = visible_to | User.objects.filter(id=self.user.id)

        cleaned_data['visible_to'] = visible_to
        return cleaned_data


class UpdateRecordForm(forms.ModelForm):
    assigned_to = forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=forms.Select(attrs={"class": "form-control"}),
        required=False
    )
    follow_up_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', "class": "form-control"}),
        required=False,
        label='Follow-Up Date & Time'
    )
    lead_source = forms.ChoiceField(
        choices=Record.LEAD_SOURCE_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Lead Source"
    )
    priority = forms.ChoiceField(
        choices=Record.PRIORITY_CHOICES,
        required=True,
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Priority"
    )
    value = forms.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={"placeholder": "Value", "class": "form-control"}),
        label="Value"
    )
    attachment = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={"class": "form-control"}),
        label="Attachment"
    )

    class Meta:
        model = Record
        fields = ['company', 'client_name', 'dept_name', 'phone', 'email', 'city', 'address', 'classification',
                  'assigned_to', 'visible_to', 'follow_up_date', 'comments', 'remarks', 'social_media_details',
                  'lead_source', 'value', 'attachment']
        widgets = {
            'visible_to': forms.CheckboxSelectMultiple(),
            'created_by': forms.HiddenInput(),
            'classification': forms.Select(choices=[
                ('assigned', 'Assigned'),
                ('unassigned', 'Unassigned'),
                ('dead', 'Dead'),
                ('in_progress', 'In Progress'),
            ], attrs={"class": "form-control"})
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.user:
            self.fields['created_by'].initial = self.user.username
            self.fields['created_by'].widget = forms.HiddenInput()


class AddTicketForm(forms.ModelForm):
    title = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Title", "class": "form-control"})
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"placeholder": "Description", "class": "form-control"})
    )
    company_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Company Name", "class": "form-control"})
    )

    # Updated ticket_type field to use ChoiceField with predefined choices
    ticket_type = forms.ChoiceField(
        required=True,
        choices=Ticket.TICKET_TYPE_CHOICES,  # Use the choices defined in the model
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Ticket Type"
    )
    status = forms.ChoiceField(
        choices=Ticket.STATUS_CHOICES,  # Use the choices defined in the model
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Status"
    )
    detailed_summary = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"placeholder": "Detailed Summary", "class": "form-control"})
    )
    ticket_source = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Ticket Source", "class": "form-control"})
    )
    resolution = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"placeholder": "Resolution", "class": "form-control"})
    )
    contact_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Contact Name", "class": "form-control"})
    )

    # Updated support_mode field to use ChoiceField with predefined choices
    support_mode = forms.ChoiceField(
        required=True,
        choices=Ticket.SUPPORT_MODE_CHOICES,  # Use the choices defined in the model
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Support Mode"
    )

    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Phone", "class": "form-control"})
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={"placeholder": "Email", "class": "form-control"})
    )

    # Add assigned_to field to select users
    assigned_to = forms.ModelChoiceField(
        queryset=User.objects.all(),  # Assuming all users are eligible to be assigned
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Assign to"
    )
    due_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', "class": "form-control"}),
        required=False,
        label='Due Date & Time'
    )
    proof_of_work = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={"class": "form-control"}),
        label="Proof of Work"
    )
    customer = forms.ModelChoiceField(
        queryset=Customer.objects.all(),  # Allow selection of customers
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Select Customer"
    )

    class Meta:
        model = Ticket
        fields = '__all__'
        exclude = ("created_by", "created_at", "modified_at", "last_modified_by", "last_modified_at")


class AddMeetingRecordForm(forms.ModelForm):
    meeting_partner = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Meeting Partner", "class": "form-control"}),
        label="Meeting Partner"
    )
    products_discussed_partner = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={"placeholder": "Products Discussed by Partner", "class": "form-control"}),
        label="Products Discussed by Partner"
    )
    products_discussed_company = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={"placeholder": "Products Discussed by Company", "class": "form-control"}),
        label="Products Discussed by Company"
    )
    conclusion = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={"placeholder": "Conclusion", "class": "form-control"}),
        label="Conclusion"
    )
    follow_up_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', "class": "form-control"}),
        required=False,
        label='Follow-Up Date & Time'
    )
    speaker = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=True,
        widget=forms.Select(attrs={"class": "form-control"}),  # Corrected to use Select widget
        label="Speaker"
    )
    attendees = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(),  # Removed 'class' attribute as it's not needed
        label="Attendees"
    )
    meeting_location = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Meeting Location", "class": "form-control"}),
        label="Meeting Location"
    )

    class Meta:
        model = MeetingRecord
        fields = ['meeting_partner', 'products_discussed_partner', 'products_discussed_company', 'conclusion',
                  'follow_up_date', 'speaker', 'attendees', 'meeting_location']


class PotentialLeadForm(forms.ModelForm):
    class Meta:
        model = PotentialLead
        fields = ['company', 'client_name', 'phone', 'email', 'initial_comments', 'follow_up_date', 'conversation']
        widgets = {
            'company': forms.TextInput(attrs={"placeholder": "Company", "class": "form-control"}),
            'client_name': forms.TextInput(attrs={"placeholder": "Client Name", "class": "form-control"}),
            'phone': forms.TextInput(attrs={"placeholder": "Phone", "class": "form-control"}),
            'email': forms.EmailInput(attrs={"placeholder": "Email", "class": "form-control"}),
            'initial_comments': forms.Textarea(
                attrs={"placeholder": "Initial Comments", "class": "form-control", 'rows': 3, 'cols': 40}),
            'follow_up_date': forms.DateTimeInput(
                attrs={"placeholder": "Follow-up Date", "class": "form-control", "type": "date"}),
            'conversation': forms.Textarea(
                attrs={"placeholder": "Last Conversation", "class": "form-control", 'rows': 3, 'cols': 40}),
        }


class UpdatePotentialLeadForm(forms.ModelForm):
    additional_comments = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "placeholder": "Add additional comments...",
                "class": "form-control",
                "rows": 3,
                "cols": 40,
            }
        ),
        required=False,
        label="Additional Comments"
    )

    class Meta:
        model = PotentialLead
        fields = ['company', 'client_name', 'phone', 'email', 'initial_comments', 'follow_up_date', 'conversation', 'additional_comments']
        widgets = {
            'company': forms.TextInput(attrs={"placeholder": "Company", "class": "form-control"}),
            'client_name': forms.TextInput(attrs={"placeholder": "Client Name", "class": "form-control"}),
            'phone': forms.TextInput(attrs={"placeholder": "Phone", "class": "form-control"}),
            'email': forms.EmailInput(attrs={"placeholder": "Email", "class": "form-control"}),
            'initial_comments': forms.Textarea(attrs={"placeholder": "Comments", "class": "form-control", 'rows': 3, 'cols': 40}),
            'follow_up_date': forms.DateTimeInput(attrs={"placeholder": "Follow-up Date", "class": "form-control", "type": "datetime-local"}),
            'conversation': forms.Textarea(attrs={"placeholder": "Conversation", "class": "form-control", 'rows': 3, 'cols': 40}),
        }


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
            'company', 'client_name', 'phone', 'email', 'address', 'city',
            'dept_name', 'lead_source', 'remarks', 'comments', 'assigned_to',
            'classification', 'bank_details', 'gst_number', 'msme', 'pancard'
        ]
        widgets = {
            'address': forms.TextInput(attrs={'rows': 3}),
            'remarks': forms.TextInput(attrs={'rows': 3}),
            'comments': forms.TextInput(attrs={'rows': 3}),
            'bank_details': forms.ClearableFileInput(),
            'gst_number': forms.ClearableFileInput(),
            'msme': forms.ClearableFileInput(),
            'pancard': forms.ClearableFileInput(),
        }


class CustomerUpdateForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
            'company', 'client_name', 'phone', 'email', 'address', 'city',
            'dept_name', 'lead_source', 'remarks', 'comments', 'assigned_to',
            'classification', 'bank_details', 'gst_number', 'msme', 'pancard'
        ]
        widgets = {
            'address': forms.TextInput(attrs={'rows': 3}),
            'remarks': forms.TextInput(attrs={'rows': 3}),
            'comments': forms.TextInput(attrs={'rows': 3}),
            'bank_details': forms.ClearableFileInput(),
            'gst_number': forms.ClearableFileInput(),
            'msme': forms.ClearableFileInput(),
            'pancard': forms.ClearableFileInput(),
        }
