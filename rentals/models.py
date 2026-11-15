import uuid
from decimal import Decimal
from django.db import models
from django.urls import reverse
from django.utils import timezone


def generate_booking_reference():
    return f"DRV-{uuid.uuid4().hex[:8].upper()}"


class Category(models.Model):
    name = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(max_length=70, unique=True)
    description = models.TextField(blank=True)
    image_url = models.URLField(blank=True, help_text="Unsplash or external image URL")

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name


class Location(models.Model):
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=60)
    address = models.CharField(max_length=200)
    phone = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['city', 'name']

    def __str__(self):
        return f"{self.name} ({self.city})"


class Car(models.Model):
    TRANSMISSION_CHOICES = [
        ('Automatic', 'Automatic'),
        ('Manual', 'Manual'),
    ]

    FUEL_CHOICES = [
        ('Petrol', 'Petrol'),
        ('Diesel', 'Diesel'),
        ('Hybrid', 'Hybrid'),
        ('Electric', 'Electric'),
    ]

    brand = models.CharField(max_length=60)
    model_name = models.CharField(max_length=60)
    year = models.PositiveIntegerField(default=2024)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='cars')
    license_plate = models.CharField(max_length=20, unique=True)
    daily_rate = models.DecimalField(max_digits=10, decimal_places=2, help_text="Daily rental price in USD")
    transmission = models.CharField(max_length=20, choices=TRANSMISSION_CHOICES, default='Automatic')
    fuel_type = models.CharField(max_length=20, choices=FUEL_CHOICES, default='Petrol')
    seats = models.PositiveIntegerField(default=5)
    doors = models.PositiveIntegerField(default=4)
    luggage_capacity = models.PositiveIntegerField(default=2, help_text="Number of suitcases")
    has_air_conditioning = models.BooleanField(default=True)
    has_gps = models.BooleanField(default=True)
    has_bluetooth = models.BooleanField(default=True)
    mileage = models.PositiveIntegerField(default=15000, help_text="Odometer reading in km")
    image_url = models.URLField(blank=True, help_text="Primary image link from web / CDN")
    image = models.ImageField(upload_to='cars/', blank=True, null=True)
    description = models.TextField(blank=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_featured', 'brand', 'model_name']

    def __str__(self):
        return f"{self.brand} {self.model_name} ({self.year}) - {self.license_plate}"

    @property
    def display_name(self):
        return f"{self.brand} {self.model_name}"

    @property
    def photo_url(self):
        if self.image:
            return self.image.url
        if self.image_url:
            return self.image_url
        return "https://images.unsplash.com/photo-1549399542-7e3f8b79c341?auto=format&fit=crop&w=800&q=80"

    def is_available(self, start_date, end_date, exclude_booking_id=None):
        if not self.is_active:
            return False
        if not start_date or not end_date:
            return True
        
        conflicts = Booking.objects.filter(
            car=self,
            status__in=['PENDING', 'CONFIRMED', 'ACTIVE'],
            pickup_date__lt=end_date,
            return_date__gt=start_date
        )
        if exclude_booking_id:
            conflicts = conflicts.exclude(id=exclude_booking_id)
        return not conflicts.exists()


class Booking(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending Confirmation'),
        ('CONFIRMED', 'Confirmed'),
        ('ACTIVE', 'Active (Picked Up)'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    booking_reference = models.CharField(
        max_length=30,
        unique=True,
        default=generate_booking_reference,
        editable=False
    )
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='bookings')
    customer_name = models.CharField(max_length=120)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=30)
    customer_driver_license = models.CharField(max_length=50)

    pickup_location = models.ForeignKey(Location, on_delete=models.PROTECT, related_name='pickup_bookings')
    return_location = models.ForeignKey(Location, on_delete=models.PROTECT, related_name='return_bookings')

    pickup_date = models.DateField()
    pickup_time = models.CharField(max_length=10, default="10:00 AM")
    return_date = models.DateField()
    return_time = models.CharField(max_length=10, default="10:00 AM")

    total_days = models.PositiveIntegerField(default=1)
    daily_rate_applied = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='CONFIRMED')
    special_requests = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.booking_reference} - {self.customer_name} ({self.car.display_name})"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.pickup_date and self.return_date:
            if self.return_date <= self.pickup_date:
                raise ValidationError("Return date must be after pickup date.")

    def save(self, *args, **kwargs):
        if self.pickup_date and self.return_date:
            delta = (self.return_date - self.pickup_date).days
            self.total_days = max(delta, 1)
        if not self.daily_rate_applied and self.car:
            self.daily_rate_applied = self.car.daily_rate
        if self.daily_rate_applied and self.total_days:
            self.total_amount = Decimal(self.daily_rate_applied) * Decimal(self.total_days)
        super().save(*args, **kwargs)
