from datetime import date
from django import forms
from .models import Booking, Location, Car


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
        super().__init__(*args, **kwargs)
        self.fields['pickup_location'].queryset = Location.objects.filter(is_active=True)
        self.fields['return_location'].queryset = Location.objects.filter(is_active=True)

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
