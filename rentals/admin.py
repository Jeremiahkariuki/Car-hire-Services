from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Category, Location, Car, Booking, CustomerProfile, VehicleInspection, MaintenanceRecord

admin.site.site_header = "RideKari Car Hire Admin"
admin.site.site_title = "RideKari Portal"
admin.site.index_title = "Fleet & Reservation Management"


class CustomerProfileInline(admin.StackedInline):
    model = CustomerProfile
    can_delete = False
    verbose_name_plural = 'Customer Profile'


# Re-register UserAdmin to include CustomerProfile
User = get_user_model()
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = (CustomerProfileInline,)


class VehicleInspectionInline(admin.TabularInline):
    model = VehicleInspection
    extra = 0
    fields = ('inspection_type', 'odometer_reading', 'fuel_level', 'exterior_condition', 'interior_condition', 'has_all_documents', 'created_at')
    readonly_fields = ('created_at',)


class MaintenanceRecordInline(admin.TabularInline):
    model = MaintenanceRecord
    extra = 0
    fields = ('service_type', 'status', 'service_date', 'next_service_due_date', 'next_service_due_km', 'cost', 'service_provider')


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
        'mileage_formatted',
        'daily_rate',
        'transmission',
        'fuel_type',
        'service_status_badge',
        'is_featured',
        'is_active',
    )
    list_filter = ('category', 'transmission', 'fuel_type', 'is_featured', 'is_active', 'year')
    search_fields = ('brand', 'model_name', 'license_plate')
    list_editable = ('daily_rate', 'is_featured', 'is_active')
    inlines = [MaintenanceRecordInline]
    readonly_fields = ('image_preview',)

    fieldsets = (
        ('🚗 Vehicle Identity', {
            'fields': (
                ('brand', 'model_name', 'year'),
                ('license_plate', 'category'),
            )
        }),
        ('💰 Pricing & Status', {
            'fields': (
                ('daily_rate',),
                ('is_active', 'is_featured'),
            )
        }),
        ('⚙️ Specifications', {
            'fields': (
                ('transmission', 'fuel_type'),
                ('seats', 'doors', 'luggage_capacity'),
                ('has_air_conditioning', 'has_gps', 'has_bluetooth'),
                ('mileage',),
            )
        }),
        ('🖼️ Vehicle Images', {
            'description': 'Upload a photo directly or paste a web image URL. Upload takes priority.',
            'fields': (
                'image_preview',
                'image',
                'image_url',
            )
        }),
        ('📝 Description', {
            'fields': ('description',),
            'classes': ('collapse',),
        }),
    )

    def image_preview(self, obj):
        url = obj.photo_url
        return format_html(
            '<div style="margin: 8px 0;">'
            '<img src="{}" style="max-width: 480px; max-height: 280px; object-fit: cover; '
            'border-radius: 12px; border: 2px solid #e2e8f0; box-shadow: 0 4px 6px rgba(0,0,0,0.1);" />'
            '<p style="font-size: 11px; color: #64748b; margin-top: 6px;">📸 Current vehicle image — '
            'upload a new file below or change the URL to update it.</p>'
            '</div>',
            url
        )
    image_preview.short_description = "Current Image Preview"

    def thumbnail(self, obj):
        url = obj.photo_url
        return format_html(
            '<img src="{}" style="width: 60px; height: 40px; object-fit: cover; border-radius: 4px;" />',
            url
        )
    thumbnail.short_description = "Vehicle"

    def mileage_formatted(self, obj):
        return f"{obj.mileage:,} km"
    mileage_formatted.short_description = "Odometer"

    def service_status_badge(self, obj):
        if obj.overdue_maintenance:
            return format_html(
                '<span style="background-color: #ef4444; color: white; padding: 3px 8px; border-radius: 12px; font-weight: 600; font-size: 11px;">⚠️ Service Due</span>'
            )
        return format_html(
            '<span style="background-color: #10b981; color: white; padding: 3px 8px; border-radius: 12px; font-weight: 600; font-size: 11px;">✓ Good</span>'
        )
    service_status_badge.short_description = "Health"


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'booking_reference',
        'customer_name',
        'registered_account',
        'car_info',
        'pickup_date',
        'return_date',
        'total_days',
        'total_amount_formatted',
        'status_badge',
        'inspection_summary',
        'created_at',
    )
    list_filter = ('status', 'pickup_date', 'return_date', 'pickup_location')
    search_fields = ('booking_reference', 'customer_name', 'customer_email', 'customer_phone', 'customer_driver_license')
    readonly_fields = ('booking_reference', 'created_at', 'updated_at', 'total_amount')
    list_per_page = 20
    inlines = [VehicleInspectionInline]

    def registered_account(self, obj):
        if obj.user:
            return format_html('<span style="color: #2563eb; font-weight: 600;">@{}</span>', obj.user.username)
        return format_html('<span style="color: #9ca3af;">Guest</span>')
    registered_account.short_description = "Account"

    def car_info(self, obj):
        return f"{obj.car.display_name} ({obj.car.license_plate})"
    car_info.short_description = "Rented Car"

    def total_amount_formatted(self, obj):
        return f"KSh {obj.total_amount:,.2f}"
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

    def inspection_summary(self, obj):
        check_out = obj.inspections.filter(inspection_type='CHECK_OUT').exists()
        check_in = obj.inspections.filter(inspection_type='CHECK_IN').exists()
        if check_in:
            return format_html('<span style="color: #059669; font-weight: 600;">✓ In & Out Done</span>')
        elif check_out:
            return format_html('<span style="color: #d97706; font-weight: 600;">Out Done (Awaiting In)</span>')
        return format_html('<span style="color: #9ca3af;">Pending Inspection</span>')
    inspection_summary.short_description = "Inspections"


@admin.register(VehicleInspection)
class VehicleInspectionAdmin(admin.ModelAdmin):
    list_display = (
        'inspection_type_badge',
        'car',
        'booking',
        'odometer_formatted',
        'fuel_level',
        'exterior_condition',
        'interior_condition',
        'inspected_by',
        'created_at',
    )
    list_filter = ('inspection_type', 'fuel_level', 'exterior_condition', 'interior_condition', 'created_at')
    search_fields = ('car__brand', 'car__model_name', 'car__license_plate', 'booking__booking_reference', 'damage_notes')

    def inspection_type_badge(self, obj):
        if obj.inspection_type == 'CHECK_OUT':
            return format_html('<span style="background-color: #3b82f6; color: white; padding: 2px 7px; border-radius: 8px; font-size: 11px; font-weight: 600;">Check-Out (Pick-Up)</span>')
        return format_html('<span style="background-color: #10b981; color: white; padding: 2px 7px; border-radius: 8px; font-size: 11px; font-weight: 600;">Check-In (Return)</span>')
    inspection_type_badge.short_description = "Type"

    def odometer_formatted(self, obj):
        return f"{obj.odometer_reading:,} km"
    odometer_formatted.short_description = "Odometer"


@admin.register(MaintenanceRecord)
class MaintenanceRecordAdmin(admin.ModelAdmin):
    list_display = (
        'service_type',
        'car',
        'status_badge',
        'service_date',
        'next_service_due_date',
        'next_service_due_km',
        'cost_formatted',
        'service_provider',
        'overdue_indicator',
    )
    list_filter = ('status', 'service_type', 'service_date')
    search_fields = ('car__brand', 'car__model_name', 'car__license_plate', 'service_provider', 'notes')

    def cost_formatted(self, obj):
        return f"KSh {obj.cost:,.2f}"
    cost_formatted.short_description = "Cost"

    def status_badge(self, obj):
        colors = {
            'SCHEDULED': '#f59e0b',
            'IN_PROGRESS': '#3b82f6',
            'COMPLETED': '#10b981',
            'CANCELLED': '#ef4444',
        }
        color = colors.get(obj.status, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 7px; border-radius: 8px; font-weight: 600; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = "Status"

    def overdue_indicator(self, obj):
        if obj.is_overdue:
            return format_html('<span style="color: #ef4444; font-weight: 700;">⚠️ Overdue</span>')
        return format_html('<span style="color: #10b981;">✓ On Schedule</span>')
    overdue_indicator.short_description = "Schedule"


# ========================================================
# Custom Dashboard Index Context
# ========================================================
original_admin_index = admin.site.index

def custom_admin_index(request, extra_context=None):
    extra = extra_context or {}
    total_cars = Car.objects.count()
    available_cars = Car.objects.filter(is_active=True).count()
    total_bookings = Booking.objects.count()
    active_bookings = Booking.objects.filter(status__in=['CONFIRMED', 'ACTIVE', 'PENDING']).count()
    total_inspections = VehicleInspection.objects.count()
    maintenance_records = MaintenanceRecord.objects.all()
    overdue_maintenance = sum(1 for m in maintenance_records if m.is_overdue)
    recent_bookings = Booking.objects.select_related('car', 'pickup_location').order_by('-created_at')[:6]
    recent_cars = Car.objects.select_related('category').order_by('-created_at')[:4]

    extra.update({
        'total_cars': total_cars,
        'available_cars': available_cars,
        'total_bookings': total_bookings,
        'active_bookings': active_bookings,
        'total_inspections': total_inspections,
        'overdue_maintenance': overdue_maintenance,
        'recent_bookings': recent_bookings,
        'recent_cars': recent_cars,
    })
    return original_admin_index(request, extra_context=extra)

admin.site.index = custom_admin_index
