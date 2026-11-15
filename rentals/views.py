from datetime import datetime, date
from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from .models import Car, Category, Location, Booking
from .forms import BookingForm, QuickSearchForm, BookingLookupForm


def home(request):
    featured_cars = Car.objects.filter(is_active=True, is_featured=True)[:6]
    if not featured_cars.exists():
        featured_cars = Car.objects.filter(is_active=True)[:6]
    categories = Category.objects.all()
    locations = Location.objects.filter(is_active=True)
    search_form = QuickSearchForm()
    
    return render(request, 'rentals/home.html', {
        'featured_cars': featured_cars,
        'categories': categories,
        'locations': locations,
        'search_form': search_form,
    })


def car_list(request):
    cars = Car.objects.filter(is_active=True)
    categories = Category.objects.all()
    locations = Location.objects.filter(is_active=True)

    # Filtering parameters
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
        form = BookingForm(request.POST, car=car)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.car = car
            booking.daily_rate_applied = car.daily_rate
            booking.save()
            messages.success(request, f"Your reservation is confirmed! Booking Reference: {booking.booking_reference}")
            return redirect('booking_confirmation', ref=booking.booking_reference)
    else:
        form = BookingForm(car=car, initial=initial_data)

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
        if booking.status in ['PENDING', 'CONFIRMED']:
            booking.status = 'CANCELLED'
            booking.save()
            messages.success(request, f"Booking {booking.booking_reference} has been cancelled successfully.")
        else:
            messages.warning(request, f"Cannot cancel booking with current status: {booking.get_status_display()}")
        return redirect('booking_lookup')
    return redirect('home')


def about(request):
    locations = Location.objects.filter(is_active=True)
    return render(request, 'rentals/about.html', {'locations': locations})
