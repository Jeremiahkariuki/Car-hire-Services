# DriveEasy - Car Hire & Rental System

A modern full-stack Car Hire and Fleet Management System built with **Python 3**, **Django 5**, **SQLite**, and **Tailwind CSS**.

---

## 🌟 Key Features

### 🚗 Customer Booking Portal
- **Interactive Home Page**: Quick search widget with pickup/return date pickers, branch locations, and category filters.
- **Dynamic Fleet Catalog**: Filter cars by Category (SUV, Luxury, Electric, Sedan, Economy, Convertible), Transmission (Automatic/Manual), Fuel Type (Petrol, Diesel, Hybrid, Electric), and maximum price.
- **Real-Time Availability & Overlap Protection**: Automatically prevents double bookings for overlapping dates.
- **Detailed Vehicle View**: Specs grid (passengers, luggage, transmission, fuel, GPS, A/C, Bluetooth, mileage), high-resolution imagery, and pricing breakdown.
- **Live Price Estimation**: Dynamic JavaScript calculator instantly displays total rental days and estimated amount as dates change.
- **Printable Booking Voucher**: Generates unique booking reference numbers (e.g. `DRV-A8F4B912`) with printable receipts.
- **Self-Service Reservation Tracking**: Customers can check reservation status or cancel reservations using their reference code and email.

### 🛡️ Admin & Fleet Management (`/admin/`)
- Preconfigured superuser credentials ready for immediate use.
- **Car Management**: Vehicle images/thumbnails, status toggles (`is_active`, `is_featured`), and real-time inline rate editing.
- **Reservation Tracking**: Color-coded badges for booking statuses (`Pending`, `Confirmed`, `Active`, `Completed`, `Cancelled`).
- **Location & Category Controls**: Add and edit rental pickup hubs and vehicle categories.

---

## 🚀 Quick Start Guide

### 1. Activate Environment & Run Development Server
```bash
# Activate the virtual environment
source venv/bin/activate

# Run database migrations (already applied)
python manage.py migrate

# (Optional) Re-seed sample cars, locations, and admin user
python manage.py seed_data

# Start the server
python manage.py runserver
```

### 2. Access the Application
- **Customer Portal**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Vehicle Catalog**: [http://127.0.0.1:8000/cars/](http://127.0.0.1:8000/cars/)
- **Reservation Lookup**: [http://127.0.0.1:8000/booking/lookup/](http://127.0.0.1:8000/booking/lookup/)
- **Admin Dashboard**: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
  - **Username**: `admin`
  - **Password**: `admin123`

---

## 🧪 Running Automated Tests

A comprehensive test suite verifies routes, booking creation, overlap conflict prevention, and cancellations:

```bash
python manage.py test
```

---

## 📂 Project Structure

```
.
├── config/                  # Django project configuration (settings, urls, wsgi)
├── rentals/                 # Car hire application
│   ├── management/commands/ # Data seeding script (seed_data.py)
│   ├── admin.py             # Custom Django Admin panel
│   ├── forms.py             # Booking & search forms with date validation
│   ├── models.py            # Category, Location, Car, Booking models
│   ├── tests.py             # Automated unit and integration tests
│   ├── urls.py              # Application routing
│   └── views.py             # Customer portal & booking logic
├── templates/               # Responsive HTML templates with Tailwind CSS
│   ├── base.html            # Navigation bar, alerts & footer
│   └── rentals/
│       ├── home.html        # Landing page with hero search
│       ├── car_list.html    # Filterable vehicle catalog
│       ├── car_detail.html  # Vehicle specs & booking form
│       ├── booking_confirmation.html # Printable voucher
│       ├── booking_lookup.html       # Self-service tracking & cancellation
│       └── about.html       # Locations network & FAQ
├── static/                  # Static assets
├── media/                   # Uploaded vehicle photos
├── db.sqlite3               # Pre-populated SQLite database
└── venv/                    # Python virtual environment
```
