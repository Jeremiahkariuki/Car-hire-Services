import uuid
from decimal import Decimal
from datetime import date
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver


def generate_booking_reference():
    return f"DRV-{uuid.uuid4().hex[:8].upper()}"


class CustomerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='customer_profile')
    phone = models.CharField(max_length=30, blank=True)
    driver_license = models.CharField(max_length=50, blank=True)
    address = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=60, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Profile of {self.user.username}"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_customer_profile(sender, instance, created, **kwargs):
    if created:
        CustomerProfile.objects.get_or_create(user=instance)


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

    @property
    def overdue_maintenance(self):
        today = date.today()
        records = self.maintenance_records.filter(status__in=['SCHEDULED', 'IN_PROGRESS'])
        for rec in records:
            if rec.next_service_due_date and rec.next_service_due_date <= today:
                return True
            if rec.next_service_due_km and self.mileage >= rec.next_service_due_km:
                return True
        return False


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
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bookings'
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


class VehicleInspection(models.Model):
    INSPECTION_TYPES = [
        ('CHECK_OUT', 'Pick-up / Check-Out'),
        ('CHECK_IN', 'Return / Check-In'),
    ]

    FUEL_LEVELS = [
        ('EMPTY', 'Empty'),
        ('QUARTER', '1/4 Tank'),
        ('HALF', '1/2 Tank'),
        ('THREE_QUARTERS', '3/4 Tank'),
        ('FULL', 'Full Tank'),
    ]

    EXTERIOR_CONDITIONS = [
        ('EXCELLENT', 'Excellent - No Scratches/Dents'),
        ('GOOD', 'Good - Minor Marks'),
        ('SCRATCHES', 'Noticeable Scratches/Scuffs'),
        ('DAMAGED', 'Visible Dents or Body Damage'),
    ]

    INTERIOR_CONDITIONS = [
        ('CLEAN', 'Clean & Sanitized'),
        ('NEEDS_CLEANING', 'Light Dirt / Needs Vacuum'),
        ('DIRTY', 'Stained Upholstery / Deep Clean Required'),
    ]

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='inspections')
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='inspections')
    inspection_type = models.CharField(max_length=20, choices=INSPECTION_TYPES)
    odometer_reading = models.PositiveIntegerField(help_text="Odometer reading in km at inspection time")
    fuel_level = models.CharField(max_length=20, choices=FUEL_LEVELS, default='FULL')
    exterior_condition = models.CharField(max_length=20, choices=EXTERIOR_CONDITIONS, default='EXCELLENT')
    interior_condition = models.CharField(max_length=20, choices=INTERIOR_CONDITIONS, default='CLEAN')
    has_spare_tire_and_jack = models.BooleanField(default=True, help_text="Spare wheel, jack and wrench present")
    has_all_documents = models.BooleanField(default=True, help_text="Vehicle registration and insurance papers present")
    damage_notes = models.TextField(blank=True, help_text="Record any scratches, chips, stains or observations")
    damage_photo = models.ImageField(upload_to='inspections/', blank=True, null=True)
    inspected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='conducted_inspections'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_inspection_type_display()} - {self.car.license_plate} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Automatically update vehicle's current odometer if inspection reading is higher
        if self.odometer_reading and self.odometer_reading > self.car.mileage:
            self.car.mileage = self.odometer_reading
            self.car.save(update_fields=['mileage'])


class MaintenanceRecord(models.Model):
    SERVICE_TYPES = [
        ('OIL_CHANGE', 'Engine Oil & Filter Change'),
        ('TIRE_ROTATION', 'Tire Rotation & Wheel Alignment'),
        ('BRAKE_SERVICE', 'Brake Pad / Disc Service'),
        ('INSPECTION', 'Scheduled Periodic Safety Inspection'),
        ('BATTERY', 'Battery Test / Replacement'),
        ('AIR_FILTER', 'Cabin & Engine Air Filters'),
        ('REPAIR', 'Mechanical / Electrical / Body Repair'),
    ]

    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='maintenance_records')
    service_type = models.CharField(max_length=30, choices=SERVICE_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED')
    service_date = models.DateField(help_text="Date service was performed or is scheduled for")
    odometer_at_service = models.PositiveIntegerField(blank=True, null=True, help_text="Odometer km at service time")
    next_service_due_date = models.DateField(blank=True, null=True, help_text="Expiry or next scheduled service date")
    next_service_due_km = models.PositiveIntegerField(blank=True, null=True, help_text="Odometer km when next service is due")
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), help_text="Service cost in USD")
    service_provider = models.CharField(max_length=120, blank=True, help_text="Workshop, dealer or mechanic name")
    notes = models.TextField(blank=True, help_text="Details of parts replaced, invoice numbers, or work done")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-service_date', '-created_at']

    def __str__(self):
        return f"{self.get_service_type_display()} - {self.car.license_plate} ({self.service_date})"

    @property
    def is_overdue(self):
        today = date.today()
        if self.status in ['SCHEDULED', 'IN_PROGRESS']:
            if self.next_service_due_date and self.next_service_due_date <= today:
                return True
            if self.next_service_due_km and self.car.mileage >= self.next_service_due_km:
                return True
        return False
