from datetime import date, timedelta
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from rentals.models import Category, Location, Car, Booking


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
            is_active=True,
            is_featured=True,
        )

    def test_homepage_loads(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Toyota Prado")

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
        # Create an existing booking
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

        # Attempt to overlap: day 7 to day 12
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
        # Form should be invalid and not redirect
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

        # Lookup
        lookup_res = self.client.post(reverse('booking_lookup'), {
            'booking_reference': booking.booking_reference,
            'email': 'alice@example.com'
        })
        self.assertEqual(lookup_res.status_code, 200)
        self.assertContains(lookup_res, booking.booking_reference)

        # Cancel
        cancel_res = self.client.post(reverse('cancel_booking', args=[booking.booking_reference]))
        self.assertEqual(cancel_res.status_code, 302)
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'CANCELLED')
