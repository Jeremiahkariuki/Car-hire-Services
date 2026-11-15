from datetime import date
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from .models import Booking, Location, Car, CustomerProfile, VehicleInspection

User = get_user_model()


class QuickSearchForm(forms.Form):
    pickup_location = forms.ModelChoiceField(
        queryset=Location.objects.filter(is_active=True),
        required=False,
        empty_label="All Pickup Locations",
        widget=forms.Select(attrs={'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-blue-600 focus:outline-none bg-white text-slate-800 text-sm'})
    )
    pickup_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-blue-600 focus:outline-none bg-white text-slate-800 text-sm'})
    )
    return_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-blue-600 focus:outline-none bg-white text-slate-800 text-sm'})
    )
    category = forms.CharField(required=False, widget=forms.HiddenInput())


class BookingForm(forms.ModelForm):
    TIME_CHOICES = [
        ('08:00 AM', '08:00 AM'),
        ('09:00 AM', '09:00 AM'),
        ('10:00 AM', '10:00 AM'),
        ('11:00 AM', '11:00 AM'),
        ('12:00 PM', '12:00 PM'),
        ('01:00 PM', '01:00 PM'),
        ('02:00 PM', '02:00 PM'),
        ('03:00 PM', '03:00 PM'),
        ('04:00 PM', '04:00 PM'),
        ('05:00 PM', '05:00 PM'),
        ('06:00 PM', '06:00 PM'),
        ('07:00 PM', '07:00 PM'),
    ]

    pickup_time = forms.ChoiceField(
        choices=TIME_CHOICES,
        initial='10:00 AM',
        widget=forms.Select(attrs={'class': 'w-full px-3.5 py-2.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-600 focus:outline-none text-sm'})
    )
    return_time = forms.ChoiceField(
        choices=TIME_CHOICES,
        initial='10:00 AM',
        widget=forms.Select(attrs={'class': 'w-full px-3.5 py-2.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-600 focus:outline-none text-sm'})
    )

    class Meta:
        model = Booking
        fields = [
            'pickup_location',
            'return_location',
            'pickup_date',
            'pickup_time',
            'return_date',
            'return_time',
            'customer_name',
            'customer_email',
            'customer_phone',
            'customer_driver_license',
            'special_requests',
        ]
        widgets = {
            'pickup_location': forms.Select(attrs={'class': 'w-full px-3.5 py-2.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-600 focus:outline-none text-sm'}),
            'return_location': forms.Select(attrs={'class': 'w-full px-3.5 py-2.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-600 focus:outline-none text-sm'}),
            'pickup_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-3.5 py-2.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-600 focus:outline-none text-sm'}),
            'return_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-3.5 py-2.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-600 focus:outline-none text-sm'}),
            'customer_name': forms.TextInput(attrs={'placeholder': 'Full Legal Name', 'class': 'w-full px-3.5 py-2.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-600 focus:outline-none text-sm'}),
            'customer_email': forms.EmailInput(attrs={'placeholder': 'you@example.com', 'class': 'w-full px-3.5 py-2.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-600 focus:outline-none text-sm'}),
            'customer_phone': forms.TextInput(attrs={'placeholder': '+1 (555) 000-0000', 'class': 'w-full px-3.5 py-2.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-600 focus:outline-none text-sm'}),
            'customer_driver_license': forms.TextInput(attrs={'placeholder': 'Driver License / Passport ID', 'class': 'w-full px-3.5 py-2.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-600 focus:outline-none text-sm'}),
            'special_requests': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Optional: Child seat, airport flight number, GPS preferences...', 'class': 'w-full px-3.5 py-2.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-600 focus:outline-none text-sm'}),
        }

    def __init__(self, *args, **kwargs):
        self.car = kwargs.pop('car', None)
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['pickup_location'].queryset = Location.objects.filter(is_active=True)
        self.fields['return_location'].queryset = Location.objects.filter(is_active=True)

        # Prepopulate customer fields if user is authenticated
        if user and user.is_authenticated:
            if not self.initial.get('customer_name'):
                full_name = f"{user.first_name} {user.last_name}".strip()
                self.initial['customer_name'] = full_name if full_name else user.username
            if not self.initial.get('customer_email'):
                self.initial['customer_email'] = user.email
            if hasattr(user, 'customer_profile'):
                profile = user.customer_profile
                if not self.initial.get('customer_phone') and profile.phone:
                    self.initial['customer_phone'] = profile.phone
                if not self.initial.get('customer_driver_license') and profile.driver_license:
                    self.initial['customer_driver_license'] = profile.driver_license

    def clean(self):
        cleaned_data = super().clean()
        p_date = cleaned_data.get('pickup_date')
        r_date = cleaned_data.get('return_date')

        if p_date and r_date:
            if p_date < date.today():
                self.add_error('pickup_date', "Pickup date cannot be in the past.")
            if r_date <= p_date:
                self.add_error('return_date', "Return date must be after the pickup date.")
            elif self.car and not self.car.is_available(p_date, r_date):
                raise forms.ValidationError("Sorry, this vehicle is already booked for the selected dates. Please choose different dates or another car.")

        return cleaned_data


class BookingLookupForm(forms.Form):
    booking_reference = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g. DRV-B4C12E79',
            'class': 'w-full px-4 py-3 rounded-xl border border-slate-300 focus:ring-2 focus:ring-blue-600 focus:outline-none text-sm uppercase font-mono'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'The email used when booking',
            'class': 'w-full px-4 py-3 rounded-xl border border-slate-300 focus:ring-2 focus:ring-blue-600 focus:outline-none text-sm'
        })
    )


class CustomerRegistrationForm(forms.ModelForm):
    first_name = forms.CharField(max_length=40, required=True, widget=forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-blue-600 focus:outline-none'}))
    last_name = forms.CharField(max_length=40, required=True, widget=forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-blue-600 focus:outline-none'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'w-full px-4 py-3 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-blue-600 focus:outline-none'}))
    phone = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'placeholder': '+1 (555) 000-0000', 'class': 'w-full px-4 py-3 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-blue-600 focus:outline-none'}))
    driver_license = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'placeholder': 'Driver License / Passport ID', 'class': 'w-full px-4 py-3 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-blue-600 focus:outline-none'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'w-full px-4 py-3 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-blue-600 focus:outline-none'}))
    password_confirm = forms.CharField(label="Confirm Password", widget=forms.PasswordInput(attrs={'class': 'w-full px-4 py-3 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-blue-600 focus:outline-none'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-blue-600 focus:outline-none'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('password_confirm')
        if p1 and p2 and p1 != p2:
            self.add_error('password_confirm', "Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            profile, _ = CustomerProfile.objects.get_or_create(user=user)
            profile.phone = self.cleaned_data['phone']
            profile.driver_license = self.cleaned_data['driver_license']
            profile.save()
            user.customer_profile = profile
        return user


class CustomerProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=40, required=True, widget=forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-blue-600 focus:outline-none'}))
    last_name = forms.CharField(max_length=40, required=True, widget=forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-blue-600 focus:outline-none'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'w-full px-4 py-3 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-blue-600 focus:outline-none'}))
    phone = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-blue-600 focus:outline-none'}))
    driver_license = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-blue-600 focus:outline-none'}))
    address = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-blue-600 focus:outline-none'}))
    city = forms.CharField(max_length=60, required=False, widget=forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-blue-600 focus:outline-none'}))

    class Meta:
        model = CustomerProfile
        fields = ['phone', 'driver_license', 'address', 'city']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
            self.fields['email'].initial = self.user.email

    def save(self, commit=True):
        profile = super().save(commit=commit)
        if self.user:
            self.user.first_name = self.cleaned_data['first_name']
            self.user.last_name = self.cleaned_data['last_name']
            self.user.email = self.cleaned_data['email']
            self.user.save()
        return profile


class VehicleInspectionForm(forms.ModelForm):
    class Meta:
        model = VehicleInspection
        fields = [
            'inspection_type',
            'odometer_reading',
            'fuel_level',
            'exterior_condition',
            'interior_condition',
            'has_spare_tire_and_jack',
            'has_all_documents',
            'damage_notes',
            'damage_photo',
        ]
        widgets = {
            'inspection_type': forms.Select(attrs={'class': 'w-full px-3.5 py-2.5 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-blue-600 focus:outline-none'}),
            'odometer_reading': forms.NumberInput(attrs={'class': 'w-full px-3.5 py-2.5 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-blue-600 focus:outline-none'}),
            'fuel_level': forms.Select(attrs={'class': 'w-full px-3.5 py-2.5 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-blue-600 focus:outline-none'}),
            'exterior_condition': forms.Select(attrs={'class': 'w-full px-3.5 py-2.5 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-blue-600 focus:outline-none'}),
            'interior_condition': forms.Select(attrs={'class': 'w-full px-3.5 py-2.5 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-blue-600 focus:outline-none'}),
            'damage_notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Detailed observations on scratches, dents, condition...', 'class': 'w-full px-3.5 py-2.5 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-blue-600 focus:outline-none'}),
        }
