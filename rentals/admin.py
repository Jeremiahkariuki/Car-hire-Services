from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Location, Car, Booking

admin.site.site_header = "DriveEasy Car Hire Admin"
admin.site.site_title = "DriveEasy Portal"
admin.site.index_title = "Fleet & Reservation Management"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'cars_count')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

    def cars_count(self, obj):
        return obj.cars.count()
    cars_count.short_description = "Total Cars"


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'address', 'phone', 'is_active')
    list_filter = ('city', 'is_active')
    search_fields = ('name', 'city', 'address')


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = (
        'thumbnail',
        'display_name',
        'year',
        'category',
        'license_plate',
        'daily_rate',
        'transmission',
        'fuel_type',
        'is_featured',
        'is_active',
    )
    list_filter = ('category', 'transmission', 'fuel_type', 'is_featured', 'is_active', 'year')
    search_fields = ('brand', 'model_name', 'license_plate')
    list_editable = ('daily_rate', 'is_featured', 'is_active')

    def thumbnail(self, obj):
        url = obj.photo_url
        return format_html(
            '<img src="{}" style="width: 60px; height: 40px; object-fit: cover; border-radius: 4px;" />',
            url
        )
    thumbnail.short_description = "Vehicle"


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'booking_reference',
        'customer_name',
        'car_info',
        'pickup_date',
        'return_date',
        'total_days',
        'total_amount_formatted',
        'status_badge',
        'created_at',
    )
    list_filter = ('status', 'pickup_date', 'return_date', 'pickup_location')
    search_fields = ('booking_reference', 'customer_name', 'customer_email', 'customer_phone', 'customer_driver_license')
    readonly_fields = ('booking_reference', 'created_at', 'updated_at', 'total_amount')
    list_per_page = 20

    def car_info(self, obj):
        return f"{obj.car.display_name} ({obj.car.license_plate})"
    car_info.short_description = "Rented Car"

    def total_amount_formatted(self, obj):
        return f"${obj.total_amount:.2f}"
    total_amount_formatted.short_description = "Total"

    def status_badge(self, obj):
        colors = {
            'PENDING': '#f59e0b',
            'CONFIRMED': '#10b981',
            'ACTIVE': '#3b82f6',
            'COMPLETED': '#6b7280',
            'CANCELLED': '#ef4444',
        }
        color = colors.get(obj.status, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 12px; font-weight: 600; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = "Status"
