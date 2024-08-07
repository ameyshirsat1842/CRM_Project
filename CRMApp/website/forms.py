from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Record, Ticket, MeetingRecord, PotentialLead


class SignUpForm(UserCreationForm):
    email = forms.EmailField(label="",
                             widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}))
    first_name = forms.CharField(label="", max_length=100,
                                 widget=forms.TextInput(
                                     attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(label="", max_length=100,
                                widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)

        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['username'].widget.attrs['placeholder'] = 'User Name'
        self.fields['username'].label = ''
        self.fields[
            'username'].help_text = ('<span class="form-text text-muted"><small>Required. 150 characters or fewer. '
                                     'Letters, digits and @/./+/-/_ only.</small></span>')

        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['placeholder'] = 'Password'
        self.fields['password1'].label = ''
        self.fields[
            'password1'].help_text = ('<ul class="form-text text-muted small"><li>Your password can\'t be too similar '
                                      'to your other personal information.</li><li>Your password must contain at '
                                      'least 8 characters.</li><li>Your password can\'t be a commonly used '
                                      'password.</li><li>Your password can\'t be entirely numeric.</li></ul>')

        self.fields['password2'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'
        self.fields['password2'].label = ''
        self.fields[
            'password2'].help_text = ('<span class="form-text text-muted"><small>Enter the same password as before, '
                                      'for verification.</small></span>')


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
    visible_to = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    follow_up_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', "class": "form-control"}),
        required=False,
        label='Follow-Up Date'
    )
    comments = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Comments", "class": "form-control"}),
        label="Comments"
    )
    remarks = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Remarks", "class": "form-control"}),
        label="Remarks"
    )
    social_media_details = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'cols': 40, 'placeholder': 'Social Media Details', 'class': 'form-control'}),
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
        required=True,
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Lead Source"
    )

    class Meta:
        model = Record
        fields = ['company', 'client_name', 'dept_name', 'phone', 'email', 'city', 'address', 'classification',
                  'assigned_to', 'visible_to', 'follow_up_date', 'comments', 'remarks', 'social_media_details', 'lead_source']
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
    follow_up_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', "class": "form-control"}),
        required=False,
        label='Follow-Up Date'
    )
    lead_source = forms.ChoiceField(
        choices=Record.LEAD_SOURCE_CHOICES,
        required=True,
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Lead Source"
    )

    class Meta:
        model = Record
        fields = [
            'company', 'client_name', 'dept_name', 'phone', 'email', 'city',
            'address', 'assigned_to', 'follow_up_date', 'comments', 'remarks', 'visible_to', 'attachments',
            'social_media_details', 'classification', 'lead_source'
        ]
        widgets = {
            'visible_to': forms.CheckboxSelectMultiple,
            'created_by': forms.HiddenInput(),
            'classification': forms.Select(choices=[
                ('assigned', 'Assigned'),
                ('unassigned', 'Unassigned'),
                ('dead', 'Dead'),
                ('in_progress', 'In Progress'),
            ])
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['created_by'].initial = self.user.username
            self.fields['created_by'].widget = forms.HiddenInput()


class AddTicketForm(forms.ModelForm):
    title = forms.CharField(required=True,
                            widget=forms.TextInput(attrs={"placeholder": "Title", "class": "form-control"}))
    description = forms.CharField(required=False,
                                  widget=forms.Textarea(attrs={"placeholder": "Description", "class": "form-control"}))
    company_name = forms.CharField(required=True,
                                   widget=forms.TextInput(
                                       attrs={"placeholder": "Company Name", "class": "form-control"}))
    ticket_type = forms.CharField(required=True,
                                  widget=forms.TextInput(attrs={"placeholder": "Ticket Type", "class": "form-control"}))
    status = forms.CharField(required=True,
                             widget=forms.TextInput(attrs={"placeholder": "Status", "class": "form-control"}))
    account_name = forms.CharField(required=True,
                                   widget=forms.TextInput(
                                       attrs={"placeholder": "Account Name", "class": "form-control"}))
    detailed_summary = forms.CharField(required=False,
                                       widget=forms.Textarea(
                                           attrs={"placeholder": "Detailed Summary", "class": "form-control"}))
    comments_history = forms.CharField(required=False,
                                       widget=forms.Textarea(
                                           attrs={"placeholder": "Comments / History", "class": "form-control"}))
    contract = forms.CharField(required=False,
                               widget=forms.TextInput(attrs={"placeholder": "Contract", "class": "form-control"}))
    ticket_source = forms.CharField(required=False,
                                    widget=forms.TextInput(
                                        attrs={"placeholder": "Ticket Source", "class": "form-control"}))
    resolution = forms.CharField(required=False,
                                 widget=forms.Textarea(attrs={"placeholder": "Resolution", "class": "form-control"}))
    contact_name = forms.CharField(required=False,
                                   widget=forms.TextInput(
                                       attrs={"placeholder": "Contact Name", "class": "form-control"}))
    support_mode = forms.CharField(required=False,
                                   widget=forms.TextInput(
                                       attrs={"placeholder": "Support Mode", "class": "form-control"}))
    phone = forms.CharField(required=False,
                            widget=forms.TextInput(attrs={"placeholder": "Phone", "class": "form-control"}))
    email = forms.EmailField(required=False,
                             widget=forms.EmailInput(attrs={"placeholder": "Email", "class": "form-control"}))

    class Meta:
        model = Ticket
        fields = '__all__'
        exclude = ("created_by", "created_at", "modified_at")


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
    follow_up_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', "class": "form-control"}),
        required=False,
        label='Follow-Up Date'
    )
    speaker = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=True,
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Speaker"
    )
    attendees = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={"class": "form-control"}),
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
        fields = ['company', 'client_name', 'phone', 'email', 'comments']
        widgets = {
            'company': forms.TextInput(attrs={"placeholder": "Company", "class": "form-control"}),
            'client_name': forms.TextInput(attrs={"placeholder": "Client Name", "class": "form-control"}),
            'phone': forms.TextInput(attrs={"placeholder": "Phone", "class": "form-control"}),
            'email': forms.EmailInput(attrs={"placeholder": "Email", "class": "form-control"}),
            'comments': forms.Textarea(attrs={"placeholder": "Comments", "class": "form-control", 'rows': 3, 'cols': 40}),
        }
