from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Record, Ticket, MeetingRecord


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

    class Meta:
        model = Record
        fields = [
            'company', 'client_name', 'dept_name', 'phone', 'email', 'city',
            'address', 'assigned_to', 'follow_up_date', 'comments', 'remarks', 'visible_to', 'attachments', 'created_by'
        ]
        widgets = {
            'created_by': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.initial['created_by'] = self.user.username


class UpdateRecordForm(forms.ModelForm):
    assigned_to = forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=forms.Select(attrs={"class": "form-control"}),
        required=False
    )

    class Meta:
        model = Record
        fields = [
            'company', 'client_name', 'dept_name', 'phone', 'email', 'city',
            'address', 'assigned_to', 'follow_up_date', 'comments', 'remarks', 'visible_to', 'attachments'
        ]
        widgets = {
            'visible_to': forms.CheckboxSelectMultiple,
            'created_by': forms.HiddenInput(),
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
                                   widget=forms.TextInput(attrs={"placeholder": "Company Name", "class": "form-control"}))
    ticket_type = forms.CharField(required=True,
                                  widget=forms.TextInput(attrs={"placeholder": "Ticket Type", "class": "form-control"}))
    status = forms.CharField(required=True,
                             widget=forms.TextInput(attrs={"placeholder": "Status", "class": "form-control"}))
    account_name = forms.CharField(required=True,
                                   widget=forms.TextInput(attrs={"placeholder": "Account Name", "class": "form-control"}))
    detailed_summary = forms.CharField(required=False,
                                       widget=forms.Textarea(attrs={"placeholder": "Detailed Summary", "class": "form-control"}))
    comments_history = forms.CharField(required=False,
                                       widget=forms.Textarea(attrs={"placeholder": "Comments / History", "class": "form-control"}))
    contract = forms.CharField(required=False,
                               widget=forms.TextInput(attrs={"placeholder": "Contract", "class": "form-control"}))
    ticket_source = forms.CharField(required=False,
                                    widget=forms.TextInput(attrs={"placeholder": "Ticket Source", "class": "form-control"}))
    resolution = forms.CharField(required=False,
                                 widget=forms.Textarea(attrs={"placeholder": "Resolution", "class": "form-control"}))
    contact_name = forms.CharField(required=False,
                                   widget=forms.TextInput(attrs={"placeholder": "Contact Name", "class": "form-control"}))
    support_mode = forms.CharField(required=False,
                                   widget=forms.TextInput(attrs={"placeholder": "Support Mode", "class": "form-control"}))
    phone = forms.CharField(required=False,
                            widget=forms.TextInput(attrs={"placeholder": "Phone", "class": "form-control"}))
    email = forms.EmailField(required=False,
                             widget=forms.EmailInput(attrs={"placeholder": "Email", "class": "form-control"}))

    class Meta:
        model = Ticket
        fields = '__all__'
        exclude = ("created_by", "created_at", "modified_at")


class MeetingRecordForm(forms.ModelForm):
    class Meta:
        model = MeetingRecord
        fields = ['id', 'meeting_partner', 'products_discussed_partner', 'products_discussed_company', 'conclusion', 'follow_up_date']

    follow_up_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', "class": "form-control"}),
        required=False,
        label='Follow-Up Date'
    )
