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

### 👤 Customer User Accounts (`/accounts/`)
- **Self-Registration & Profile Management**: Customers can register, log in, and manage driver credentials.
- **Fast One-Click Booking**: Auto-populates legal name, email, phone number, and driver's license for logged-in travelers.
- **Customer Dashboard (`/accounts/dashboard/`)**: Shows active, upcoming, and past rental trips, with links to printable vouchers and inspection reports.

### 📋 Vehicle Check-In & Check-Out Inspections
- **Digital Condition Reports**: Staff can record starting and ending odometer readings, fuel tank levels (*Empty to Full*), exterior state, and interior cleanliness.
- **Damage & Photo Log**: Capture notes and photos of pre-existing scratches, scuffs, or dents.
- **Automatic Odometer Sync**: Check-in inspection odometer automatically updates the car's current mileage in the system.
- **Tool & Document Verification**: Checkboxes to verify spare tire, jack kit, and insurance documents.

### 🔧 Fleet Maintenance & Service Scheduling
- **Periodic Service Records**: Track oil changes, tire rotations, brake jobs, multi-point inspections, and battery tests.
- **Smart Overdue Alerts**: Flags vehicles when their scheduled service date or target mileage has been passed.
- **Health Indicators**: Direct status badges in the Django admin panel (*⚠️ Service Due* vs *✓ Good*).

### 🛡️ Admin & Fleet Management (`/admin/`)
- Preconfigured superuser credentials ready for immediate use.
- **Car Management**: Vehicle images/thumbnails, status toggles (`is_active`, `is_featured`), and real-time inline rate editing.
- **Reservation Tracking**: Color-coded badges for booking statuses (`Pending`, `Confirmed`, `Active`, `Completed`, `Cancelled`).
- **Inline Operations**: Inspect vehicles directly inside booking admin records and manage service logs inside car admin pages.

---

## 🚀 Quick Start Guide

### 1. Activate Environment & Run Development Server
```bash
# Activate the virtual environment
source venv/bin/activate

# Run database migrations
python manage.py migrate

# (Optional) Seed realistic fleet, locations, customer, and admin accounts
python manage.py seed_data

# Start the server
python manage.py runserver
```

### 2. Access the Application
- **Customer Portal**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Vehicle Catalog**: [http://127.0.0.1:8000/cars/](http://127.0.0.1:8000/cars/)
- **Customer Dashboard**: [http://127.0.0.1:8000/accounts/dashboard/](http://127.0.0.1:8000/accounts/dashboard/)
  - **Demo Customer**: `customer` / `customer123`
- **Staff Admin Dashboard**: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
  - **Admin Username**: `admin`
  - **Admin Password**: `admin123`

---

## 🧪 Running Automated Tests

10 comprehensive unit and integration tests verify routes, auth, inspection updates, overlap rejection, and maintenance alerts:

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
│   ├── admin.py             # Custom Django Admin panel with inlines & badges
│   ├── forms.py             # Booking, registration, profile & inspection forms
│   ├── models.py            # Category, Location, Car, Booking, Profile, Inspection, Maintenance
│   ├── tests.py             # 10 automated unit and integration tests
│   ├── urls.py              # Application routing (portal, accounts, operations)
│   └── views.py             # Customer portal, auth, dashboard & inspection logic
├── templates/               # Responsive HTML templates with Tailwind CSS
│   ├── base.html            # Navigation bar, user pills, alerts & footer
│   └── rentals/
│       ├── home.html        # Landing page with hero search
│       ├── car_list.html    # Filterable vehicle catalog
│       ├── car_detail.html  # Vehicle specs & booking form
│       ├── booking_confirmation.html # Printable voucher
│       ├── booking_lookup.html       # Self-service tracking & cancellation
│       ├── register.html    # Customer registration
│       ├── login.html       # Customer sign-in
│       ├── dashboard.html   # Customer trips & profile hub
│       ├── profile_edit.html# Profile details editor
│       ├── record_inspection.html   # Vehicle condition inspection tool
│       └── about.html       # Locations network & FAQ
├── static/                  # Static assets
├── media/                   # Uploaded vehicle & inspection photos
├── db.sqlite3               # Pre-populated SQLite database
└── venv/                    # Python virtual environment
```
