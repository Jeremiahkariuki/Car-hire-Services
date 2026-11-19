from datetime import date, timedelta
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from rentals.models import Category, Location, Car, Booking, VehicleInspection, MaintenanceRecord, CustomerProfile

User = get_user_model()


class CarRentalSystemTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name="SUV", slug="suv")
        self.location = Location.objects.create(
            name="Airport Terminal 1",
            city="Capital City",
            address="Concourse A",
            phone="+123456789"
        )
        self.car = Car.objects.create(
            brand="Toyota",
            model_name="Prado",
            year=2024,
            category=self.category,
            license_plate="TEST-123",
            daily_rate=Decimal("100.00"),
            transmission="Automatic",
            fuel_type="Diesel",
            seats=7,
            doors=5,
            mileage=15000,
            is_active=True,
            is_featured=True,
        )

    def test_homepage_loads(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Toyota Prado")

    def test_newly_added_vehicle_appears_on_homepage(self):
        new_car = Car.objects.create(
            brand="Subaru",
            model_name="Outback",
            year=2024,
            category=self.category,
            license_plate="SUB-999",
            daily_rate=Decimal("120.00"),
            transmission="Automatic",
            fuel_type="Petrol",
            seats=5,
            doors=5,
            mileage=5000,
            is_active=True,
            is_featured=False,
        )
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Subaru Outback")
        featured_cars = list(response.context['featured_cars'])
        self.assertEqual(featured_cars[0].id, new_car.id)

    def test_car_list_page_and_filtering(self):
        response = self.client.get(reverse('car_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Toyota Prado")

        # Filter by category
        res_cat = self.client.get(reverse('car_list') + '?category=suv')
        self.assertEqual(res_cat.status_code, 200)
        self.assertContains(res_cat, "Toyota Prado")

    def test_car_detail_page(self):
        response = self.client.get(reverse('car_detail', args=[self.car.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Toyota Prado")
        self.assertContains(response, "TEST-123")

    def test_successful_booking_creation(self):
        pickup = date.today() + timedelta(days=2)
        dropoff = date.today() + timedelta(days=5)

        post_data = {
            'pickup_location': self.location.id,
            'return_location': self.location.id,
            'pickup_date': pickup.strftime('%Y-%m-%d'),
            'pickup_time': '10:00 AM',
            'return_date': dropoff.strftime('%Y-%m-%d'),
            'return_time': '10:00 AM',
            'customer_name': 'Jane Doe',
            'customer_email': 'jane@example.com',
            'customer_phone': '+1555000111',
            'customer_driver_license': 'DL-987654321',
            'special_requests': 'GPS needed',
        }

        response = self.client.post(reverse('car_detail', args=[self.car.id]), post_data)
        self.assertEqual(response.status_code, 302)

        booking = Booking.objects.get(customer_email='jane@example.com')
        self.assertEqual(booking.car, self.car)
        self.assertEqual(booking.total_days, 3)
        self.assertEqual(booking.total_amount, Decimal("300.00"))
        self.assertEqual(booking.status, 'CONFIRMED')
        self.assertTrue(booking.booking_reference.startswith("DRV-"))

    def test_booking_conflict_rejection(self):
        p1 = date.today() + timedelta(days=5)
        r1 = date.today() + timedelta(days=10)
        Booking.objects.create(
            car=self.car,
            pickup_location=self.location,
            return_location=self.location,
            pickup_date=p1,
            return_date=r1,
            customer_name='John Existing',
            customer_email='john@example.com',
            customer_phone='12345',
            customer_driver_license='DL-1',
            total_days=5,
            daily_rate_applied=Decimal("100.00"),
            total_amount=Decimal("500.00"),
            status='CONFIRMED'
        )

        post_data = {
            'pickup_location': self.location.id,
            'return_location': self.location.id,
            'pickup_date': (date.today() + timedelta(days=7)).strftime('%Y-%m-%d'),
            'pickup_time': '10:00 AM',
            'return_date': (date.today() + timedelta(days=12)).strftime('%Y-%m-%d'),
            'return_time': '10:00 AM',
            'customer_name': 'Overlap Booker',
            'customer_email': 'overlap@example.com',
            'customer_phone': '+1555999888',
            'customer_driver_license': 'DL-22',
        }
        response = self.client.post(reverse('car_detail', args=[self.car.id]), post_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "already booked for the selected dates")

    def test_booking_lookup_and_cancel(self):
        pickup = date.today() + timedelta(days=3)
        dropoff = date.today() + timedelta(days=6)
        booking = Booking.objects.create(
            car=self.car,
            pickup_location=self.location,
            return_location=self.location,
            pickup_date=pickup,
            return_date=dropoff,
            customer_name='Alice Smith',
            customer_email='alice@example.com',
            customer_phone='555123',
            customer_driver_license='DL-88',
            status='CONFIRMED'
        )

        lookup_res = self.client.post(reverse('booking_lookup'), {
            'booking_reference': booking.booking_reference,
            'email': 'alice@example.com'
        })
        self.assertEqual(lookup_res.status_code, 200)
        self.assertContains(lookup_res, booking.booking_reference)

        cancel_res = self.client.post(reverse('cancel_booking', args=[booking.booking_reference]))
        self.assertEqual(cancel_res.status_code, 302)
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'CANCELLED')

    # ==========================================
    # Customer Accounts Tests
    # ==========================================
    def test_customer_registration_and_login(self):
        reg_data = {
            'username': 'driver99',
            'first_name': 'Carlos',
            'last_name': 'Gomez',
            'email': 'carlos@example.com',
            'phone': '+1555333444',
            'driver_license': 'DL-CARLOS-77',
            'password': 'SecurePassword123!',
            'password_confirm': 'SecurePassword123!',
        }
        response = self.client.post(reverse('register'), reg_data)
        self.assertEqual(response.status_code, 302)

        user = User.objects.get(username='driver99')
        self.assertEqual(user.first_name, 'Carlos')
        user.customer_profile.refresh_from_db()
        self.assertEqual(user.customer_profile.driver_license, 'DL-CARLOS-77')

        # Test dashboard and client portal access
        dash_response = self.client.get(reverse('customer_dashboard'))
        self.assertEqual(dash_response.status_code, 200)
        self.assertContains(dash_response, "Carlos")

        portal_response = self.client.get(reverse('client_portal'))
        self.assertEqual(portal_response.status_code, 200)
        self.assertContains(portal_response, "Client Account #")

    def test_authenticated_user_booking_links_to_account(self):
        user = User.objects.create_user(
            username='sammy',
            email='sammy@example.com',
            password='password123',
            first_name='Sammy'
        )
        self.client.login(username='sammy', password='password123')

        pickup = date.today() + timedelta(days=2)
        dropoff = date.today() + timedelta(days=4)
        post_data = {
            'pickup_location': self.location.id,
            'return_location': self.location.id,
            'pickup_date': pickup.strftime('%Y-%m-%d'),
            'pickup_time': '10:00 AM',
            'return_date': dropoff.strftime('%Y-%m-%d'),
            'return_time': '10:00 AM',
            'customer_name': 'Sammy Traveler',
            'customer_email': 'sammy@example.com',
            'customer_phone': '555-8888',
            'customer_driver_license': 'DL-SAMMY',
        }
        response = self.client.post(reverse('car_detail', args=[self.car.id]), post_data)
        self.assertEqual(response.status_code, 302)

        booking = Booking.objects.get(customer_email='sammy@example.com')
        self.assertEqual(booking.user, user)

    # ==========================================
    # Vehicle Condition Inspection Tests
    # ==========================================
    def test_vehicle_inspection_workflow(self):
        user = User.objects.create_user(username='inspector', password='pw')
        self.client.login(username='inspector', password='pw')

        booking = Booking.objects.create(
            car=self.car,
            pickup_location=self.location,
            return_location=self.location,
            pickup_date=date.today(),
            return_date=date.today() + timedelta(days=3),
            customer_name='Inspector Test',
            customer_email='insp@example.com',
            customer_phone='123',
            customer_driver_license='DL-99',
            status='CONFIRMED'
        )

        # 1. Record Check-Out Inspection
        insp_post = {
            'inspection_type': 'CHECK_OUT',
            'odometer_reading': 15000,
            'fuel_level': 'FULL',
            'exterior_condition': 'EXCELLENT',
            'interior_condition': 'CLEAN',
            'has_spare_tire_and_jack': True,
            'has_all_documents': True,
            'damage_notes': 'Clean pickup',
        }
        resp = self.client.post(reverse('record_inspection', args=[booking.booking_reference]), insp_post)
        self.assertEqual(resp.status_code, 302)
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'ACTIVE')

        # 2. Record Check-In Inspection with higher odometer reading
        return_post = {
            'inspection_type': 'CHECK_IN',
            'odometer_reading': 15450,
            'fuel_level': 'FULL',
            'exterior_condition': 'GOOD',
            'interior_condition': 'CLEAN',
            'has_spare_tire_and_jack': True,
            'has_all_documents': True,
            'damage_notes': 'Returned in great shape',
        }
        resp2 = self.client.post(reverse('record_inspection', args=[booking.booking_reference]), return_post)
        self.assertEqual(resp2.status_code, 302)
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'COMPLETED')
        self.car.refresh_from_db()
        self.assertEqual(self.car.mileage, 15450)

    # ==========================================
    # Fleet Maintenance Tests
    # ==========================================
    def test_maintenance_overdue_detection(self):
        # On schedule record
        rec_good = MaintenanceRecord.objects.create(
            car=self.car,
            service_type='OIL_CHANGE',
            status='SCHEDULED',
            service_date=date.today(),
            next_service_due_date=date.today() + timedelta(days=90),
            next_service_due_km=25000,
            cost=Decimal('100.00'),
        )
        self.assertFalse(rec_good.is_overdue)

        # Overdue record
        rec_overdue = MaintenanceRecord.objects.create(
            car=self.car,
            service_type='TIRE_ROTATION',
            status='SCHEDULED',
            service_date=date.today() - timedelta(days=10),
            next_service_due_date=date.today() - timedelta(days=2),
            cost=Decimal('50.00'),
        )
        self.assertTrue(rec_overdue.is_overdue)
        self.assertTrue(self.car.overdue_maintenance)
