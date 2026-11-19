from datetime import datetime, date
from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q
from .models import Car, Category, Location, Booking, VehicleInspection, MaintenanceRecord, CustomerProfile
from .forms import (
    BookingForm,
    QuickSearchForm,
    BookingLookupForm,
    CustomerRegistrationForm,
    CustomerProfileForm,
    VehicleInspectionForm,
)


def home(request):
    # Active fleet ordered newest first so any newly added vehicle is immediately visible on the landing page
    featured_cars = Car.objects.filter(is_active=True).order_by('-created_at', '-id')[:12]
    total_cars_count = Car.objects.filter(is_active=True).count()
    categories = Category.objects.all()
    locations = Location.objects.filter(is_active=True)
    search_form = QuickSearchForm()

    return render(request, 'rentals/home.html', {
        'featured_cars': featured_cars,
        'total_cars_count': total_cars_count,
        'categories': categories,
        'locations': locations,
        'search_form': search_form,
    })


def car_list(request):
    cars = Car.objects.filter(is_active=True)
    categories = Category.objects.all()
    locations = Location.objects.filter(is_active=True)

    search_query = request.GET.get('q', '').strip()
    category_slug = request.GET.get('category', '').strip()
    transmission = request.GET.get('transmission', '').strip()
    fuel_type = request.GET.get('fuel', '').strip()
    max_price = request.GET.get('max_price', '').strip()
    pickup_date_str = request.GET.get('pickup_date', '').strip()
    return_date_str = request.GET.get('return_date', '').strip()
    pickup_location_id = request.GET.get('pickup_location', '').strip()
    sort = request.GET.get('sort', 'recommended')

    p_date = None
    r_date = None
    if pickup_date_str and return_date_str:
        try:
            p_date = datetime.strptime(pickup_date_str, '%Y-%m-%d').date()
            r_date = datetime.strptime(return_date_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    if search_query:
        cars = cars.filter(
            Q(brand__icontains=search_query) |
            Q(model_name__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )

    if category_slug:
        cars = cars.filter(category__slug=category_slug)

    if transmission:
        cars = cars.filter(transmission=transmission)

    if fuel_type:
        cars = cars.filter(fuel_type=fuel_type)

    if max_price:
        try:
            cars = cars.filter(daily_rate__lte=Decimal(max_price))
        except Exception:
            pass

    # Check date conflict
    if p_date and r_date and r_date > p_date:
        conflicting_car_ids = Booking.objects.filter(
            status__in=['PENDING', 'CONFIRMED', 'ACTIVE'],
            pickup_date__lt=r_date,
            return_date__gt=p_date
        ).values_list('car_id', flat=True)
        cars = cars.exclude(id__in=conflicting_car_ids)

    # Sorting
    if sort == 'price_low':
        cars = cars.order_by('daily_rate')
    elif sort == 'price_high':
        cars = cars.order_by('-daily_rate')
    elif sort == 'year_new':
        cars = cars.order_by('-year')
    else:
        cars = cars.order_by('-is_featured', 'brand')

    total_results = cars.count()

    return render(request, 'rentals/car_list.html', {
        'cars': cars,
        'categories': categories,
        'locations': locations,
        'total_results': total_results,
        'search_query': search_query,
        'selected_category': category_slug,
        'selected_transmission': transmission,
        'selected_fuel': fuel_type,
        'selected_max_price': max_price,
        'pickup_date': pickup_date_str,
        'return_date': return_date_str,
        'pickup_location': pickup_location_id,
        'sort': sort,
    })


def car_detail(request, pk):
    car = get_object_or_404(Car, pk=pk, is_active=True)
    similar_cars = Car.objects.filter(category=car.category, is_active=True).exclude(pk=car.pk)[:3]

    initial_data = {}
    p_date_str = request.GET.get('pickup_date')
    r_date_str = request.GET.get('return_date')
    loc_id = request.GET.get('pickup_location')

    if p_date_str:
        initial_data['pickup_date'] = p_date_str
    if r_date_str:
        initial_data['return_date'] = r_date_str
    if loc_id:
        try:
            loc = Location.objects.get(pk=loc_id, is_active=True)
            initial_data['pickup_location'] = loc
            initial_data['return_location'] = loc
        except Location.DoesNotExist:
            pass

    if request.method == 'POST':
        form = BookingForm(request.POST, car=car, user=request.user)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.car = car
            booking.daily_rate_applied = car.daily_rate
            if request.user.is_authenticated:
                booking.user = request.user
            booking.save()
            messages.success(request, f"Your reservation is confirmed! Booking Reference: {booking.booking_reference}")
            return redirect('booking_confirmation', ref=booking.booking_reference)
    else:
        form = BookingForm(car=car, initial=initial_data, user=request.user)

    return render(request, 'rentals/car_detail.html', {
        'car': car,
        'form': form,
        'similar_cars': similar_cars,
        'p_date_initial': p_date_str,
        'r_date_initial': r_date_str,
    })


def booking_confirmation(request, ref):
    booking = get_object_or_404(Booking, booking_reference=ref)
    return render(request, 'rentals/booking_confirmation.html', {
        'booking': booking
    })


def booking_lookup(request):
    booking = None
    if request.method == 'POST':
        form = BookingLookupForm(request.POST)
        if form.is_valid():
            ref = form.cleaned_data['booking_reference'].strip().upper()
            email = form.cleaned_data['email'].strip().lower()
            try:
                booking = Booking.objects.get(booking_reference=ref, customer_email__iexact=email)
            except Booking.DoesNotExist:
                messages.error(request, f"No reservation was found for code '{ref}' and email '{email}'.")
    else:
        form = BookingLookupForm()

    return render(request, 'rentals/booking_lookup.html', {
        'form': form,
        'booking': booking,
    })


def cancel_booking(request, ref):
    if request.method == 'POST':
        booking = get_object_or_404(Booking, booking_reference=ref)
        # Verify ownership if user is logged in
        if booking.user and request.user.is_authenticated and booking.user != request.user and not request.user.is_staff:
            messages.error(request, "You are not authorized to cancel this booking.")
            return redirect('customer_dashboard')

        if booking.status in ['PENDING', 'CONFIRMED']:
            booking.status = 'CANCELLED'
            booking.save()
            messages.success(request, f"Booking {booking.booking_reference} has been cancelled successfully.")
        else:
            messages.warning(request, f"Cannot cancel booking with current status: {booking.get_status_display()}")
        
        if request.user.is_authenticated:
            return redirect('customer_dashboard')
        return redirect('booking_lookup')
    return redirect('home')


# ========================================================
# Customer User Accounts Views
# ========================================================

def register_view(request):
    if request.user.is_authenticated:
        return redirect('customer_dashboard')

    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to RideKari, {user.first_name or user.username}! Your account has been created.")
            return redirect('customer_dashboard')
    else:
        form = CustomerRegistrationForm()

    return render(request, 'rentals/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('/admin/')
        return redirect('customer_dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            if user.is_staff:
                return redirect('/admin/')
            return redirect('customer_dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'rentals/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')


@login_required
def customer_dashboard(request):
    profile, _ = CustomerProfile.objects.get_or_create(user=request.user)
    bookings = request.user.bookings.all().order_by('-created_at')
    active_bookings = bookings.filter(status__in=['CONFIRMED', 'ACTIVE', 'PENDING'])
    past_bookings = bookings.filter(status__in=['COMPLETED', 'CANCELLED'])

    # SaaS client metrics
    total_spent = sum(
        (b.total_amount for b in bookings.filter(status__in=['CONFIRMED', 'ACTIVE', 'COMPLETED'])),
        Decimal('0.00')
    )
    inspections = VehicleInspection.objects.filter(booking__user=request.user).order_by('-created_at')
    active_trip = active_bookings.first()
    quick_fleet = Car.objects.filter(is_active=True).order_by('-created_at')[:4]

    return render(request, 'rentals/dashboard.html', {
        'profile': profile,
        'bookings': bookings,
        'active_bookings': active_bookings,
        'past_bookings': past_bookings,
        'active_trip': active_trip,
        'total_spent': total_spent,
        'inspections_count': inspections.count(),
        'inspections': inspections[:5],
        'quick_fleet': quick_fleet,
    })


@login_required
def profile_edit(request):
    profile, _ = CustomerProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = CustomerProfileForm(request.POST, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('customer_dashboard')
    else:
        form = CustomerProfileForm(instance=profile, user=request.user)

    return render(request, 'rentals/profile_edit.html', {'form': form})


# ========================================================
# Fleet & Inspection Operations
# ========================================================

@login_required
def record_inspection(request, booking_ref):
    booking = get_object_or_404(Booking, booking_reference=booking_ref)
    existing_inspections = booking.inspections.all()

    if request.method == 'POST':
        form = VehicleInspectionForm(request.POST, request.FILES)
        if form.is_valid():
            inspection = form.save(commit=False)
            inspection.booking = booking
            inspection.car = booking.car
            inspection.inspected_by = request.user
            inspection.save()

            # If check-out was performed, can mark booking active
            if inspection.inspection_type == 'CHECK_OUT' and booking.status == 'CONFIRMED':
                booking.status = 'ACTIVE'
                booking.save()
            # If check-in was performed, can mark booking completed
            elif inspection.inspection_type == 'CHECK_IN' and booking.status == 'ACTIVE':
                booking.status = 'COMPLETED'
                booking.save()

            messages.success(request, f"{inspection.get_inspection_type_display()} condition report saved successfully!")
            return redirect('record_inspection', booking_ref=booking.booking_reference)
    else:
        initial_data = {'odometer_reading': booking.car.mileage}
        form = VehicleInspectionForm(initial=initial_data)

    return render(request, 'rentals/record_inspection.html', {
        'booking': booking,
        'form': form,
        'existing_inspections': existing_inspections,
    })


def about(request):
    locations = Location.objects.filter(is_active=True)
    return render(request, 'rentals/about.html', {'locations': locations})
