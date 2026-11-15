from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from rentals.models import Category, Location, Car, Booking

User = get_user_model()

class Command(BaseCommand):
    help = "Seeds database with realistic rental cars, locations, categories, and an admin user."

    def handle(self, *args, **options):
        self.stdout.write("Seeding car hire database...")

        # 1. Superuser
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@driveeasy.local", "admin123")
            self.stdout.write(self.style.SUCCESS("Created admin user: username=admin, password=admin123"))
        else:
            self.stdout.write("Admin user already exists.")

        # 2. Locations
        locations_data = [
            {
                "name": "International Airport - Terminal 1",
                "city": "Capital City",
                "address": "Departures Level, Car Rental Concourse A",
                "phone": "+1 (800) 555-0101"
            },
            {
                "name": "Downtown Central Station Hub",
                "city": "Capital City",
                "address": "450 Grand Avenue, Suite 100",
                "phone": "+1 (800) 555-0102"
            },
            {
                "name": "Westside Marina & Hotel Hub",
                "city": "Westport",
                "address": "12 Ocean Boulevard",
                "phone": "+1 (800) 555-0103"
            },
            {
                "name": "Financial District Plaza",
                "city": "Capital City",
                "address": "88 Commerce Street",
                "phone": "+1 (800) 555-0104"
            },
        ]

        locations = {}
        for l_data in locations_data:
            loc, _ = Location.objects.get_or_create(
                name=l_data["name"],
                defaults=l_data
            )
            locations[loc.name] = loc
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(locations)} locations."))

        # 3. Categories
        categories_data = [
            {
                "name": "SUV & Crossover",
                "slug": "suv",
                "description": "High riding comfort, spacious cabins, and all-weather capability for road adventures.",
                "image_url": "https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?auto=format&fit=crop&w=800&q=80"
            },
            {
                "name": "Luxury & Executive",
                "slug": "luxury",
                "description": "First-class prestige, whisper-quiet performance, and cutting-edge automotive elegance.",
                "image_url": "https://images.unsplash.com/photo-1563720223185-11003d516935?auto=format&fit=crop&w=800&q=80"
            },
            {
                "name": "Electric & Hybrid",
                "slug": "electric",
                "description": "Eco-friendly zero-emissions driving with instant torque and cutting-edge tech.",
                "image_url": "https://images.unsplash.com/photo-1560958089-b8a1929cea89?auto=format&fit=crop&w=800&q=80"
            },
            {
                "name": "Economy & Compact",
                "slug": "economy",
                "description": "Zippy city cruisers with exceptional fuel economy, easy parking, and unbeatable rental rates.",
                "image_url": "https://images.unsplash.com/photo-1549399542-7e3f8b79c341?auto=format&fit=crop&w=800&q=80"
            },
            {
                "name": "Sedan & Saloon",
                "slug": "sedan",
                "description": "Smooth highway cruisers with spacious boots, great comfort, and high reliability.",
                "image_url": "https://images.unsplash.com/photo-1617814076367-b759c7d7e738?auto=format&fit=crop&w=800&q=80"
            },
            {
                "name": "Convertible & Sports",
                "slug": "convertible",
                "description": "Feel the open sky and high horsepower for unforgettable scenic weekend drives.",
                "image_url": "https://images.unsplash.com/photo-1584345604476-8ec5e12e42dd?auto=format&fit=crop&w=800&q=80"
            },
        ]

        categories = {}
        for c_data in categories_data:
            cat, _ = Category.objects.get_or_create(
                slug=c_data["slug"],
                defaults=c_data
            )
            categories[cat.slug] = cat
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(categories)} categories."))

        # 4. Cars
        cars_data = [
            {
                "brand": "Toyota",
                "model_name": "Land Cruiser Prado",
                "year": 2024,
                "category": categories["suv"],
                "license_plate": "KDA-482M",
                "daily_rate": Decimal("110.00"),
                "transmission": "Automatic",
                "fuel_type": "Diesel",
                "seats": 7,
                "doors": 5,
                "luggage_capacity": 4,
                "has_air_conditioning": True,
                "has_gps": True,
                "has_bluetooth": True,
                "mileage": 14200,
                "image_url": "https://images.unsplash.com/photo-1594502184342-2e12f877aa73?auto=format&fit=crop&w=1000&q=80",
                "description": "The ultimate full-size 4x4 SUV. Commanding driving position, plush leather seating for up to 7 passengers, and robust four-wheel drive suitable for all terrains.",
                "is_featured": True,
            },
            {
                "brand": "Tesla",
                "model_name": "Model 3 Long Range",
                "year": 2024,
                "category": categories["electric"],
                "license_plate": "EV-990-TX",
                "daily_rate": Decimal("95.00"),
                "transmission": "Automatic",
                "fuel_type": "Electric",
                "seats": 5,
                "doors": 4,
                "luggage_capacity": 3,
                "has_air_conditioning": True,
                "has_gps": True,
                "has_bluetooth": True,
                "mileage": 8500,
                "image_url": "https://images.unsplash.com/photo-1560958089-b8a1929cea89?auto=format&fit=crop&w=1000&q=80",
                "description": "Zero emissions, instant electric acceleration, and cutting-edge Autopilot assistance. Includes access to Tesla Supercharging networks nationwide.",
                "is_featured": True,
            },
            {
                "brand": "Mercedes-Benz",
                "model_name": "E-Class AMG Line",
                "year": 2024,
                "category": categories["luxury"],
                "license_plate": "MB-2024-EX",
                "daily_rate": Decimal("145.00"),
                "transmission": "Automatic",
                "fuel_type": "Petrol",
                "seats": 5,
                "doors": 4,
                "luggage_capacity": 3,
                "has_air_conditioning": True,
                "has_gps": True,
                "has_bluetooth": True,
                "mileage": 6200,
                "image_url": "https://images.unsplash.com/photo-1618843479313-40f8afb4b4d8?auto=format&fit=crop&w=1000&q=80",
                "description": "Sophisticated executive saloon with ambient cabin lighting, Burmester surround sound, and smooth 9-speed automatic transmission for business and prestige.",
                "is_featured": True,
            },
            {
                "brand": "Ford",
                "model_name": "Mustang GT Convertible",
                "year": 2023,
                "category": categories["convertible"],
                "license_plate": "GT-500-US",
                "daily_rate": Decimal("130.00"),
                "transmission": "Automatic",
                "fuel_type": "Petrol",
                "seats": 4,
                "doors": 2,
                "luggage_capacity": 2,
                "has_air_conditioning": True,
                "has_gps": True,
                "has_bluetooth": True,
                "mileage": 19000,
                "image_url": "https://images.unsplash.com/photo-1584345604476-8ec5e12e42dd?auto=format&fit=crop&w=1000&q=80",
                "description": "5.0L V8 roar with an automatic soft-top. Feel the wind and sunshine as you cruise coastal highways and mountain passes.",
                "is_featured": True,
            },
            {
                "brand": "Toyota",
                "model_name": "RAV4 Hybrid AWD",
                "year": 2024,
                "category": categories["suv"],
                "license_plate": "RAV-740-HY",
                "daily_rate": Decimal("75.00"),
                "transmission": "Automatic",
                "fuel_type": "Hybrid",
                "seats": 5,
                "doors": 5,
                "luggage_capacity": 3,
                "has_air_conditioning": True,
                "has_gps": True,
                "has_bluetooth": True,
                "mileage": 12400,
                "image_url": "https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?auto=format&fit=crop&w=1000&q=80",
                "description": "Versatile all-wheel-drive compact SUV with incredible hybrid fuel efficiency (over 40 MPG). Ideal for family getaways and weekend camping.",
                "is_featured": True,
            },
            {
                "brand": "BMW",
                "model_name": "3 Series M-Sport",
                "year": 2023,
                "category": categories["sedan"],
                "license_plate": "BM-330-MS",
                "daily_rate": Decimal("90.00"),
                "transmission": "Automatic",
                "fuel_type": "Petrol",
                "seats": 5,
                "doors": 4,
                "luggage_capacity": 3,
                "has_air_conditioning": True,
                "has_gps": True,
                "has_bluetooth": True,
                "mileage": 16500,
                "image_url": "https://images.unsplash.com/photo-1555215695-3004980ad54e?auto=format&fit=crop&w=1000&q=80",
                "description": "The quintessential sports sedan. Perfect 50:50 weight balance, razor sharp handling, and dynamic driving modes.",
                "is_featured": False,
            },
            {
                "brand": "Volkswagen",
                "model_name": "Golf 8 TSI",
                "year": 2023,
                "category": categories["economy"],
                "license_plate": "VW-088-GL",
                "daily_rate": Decimal("48.00"),
                "transmission": "Automatic",
                "fuel_type": "Petrol",
                "seats": 5,
                "doors": 5,
                "luggage_capacity": 2,
                "has_air_conditioning": True,
                "has_gps": True,
                "has_bluetooth": True,
                "mileage": 22000,
                "image_url": "https://images.unsplash.com/photo-1541899481282-d53bffe3c35d?auto=format&fit=crop&w=1000&q=80",
                "description": "Europe's favorite hatchback. Nimble around city streets, highly economical on fuel, and equipped with a responsive touchscreen cockpit.",
                "is_featured": True,
            },
            {
                "brand": "Hyundai",
                "model_name": "i10 City Compact",
                "year": 2023,
                "category": categories["economy"],
                "license_plate": "HY-101-CT",
                "daily_rate": Decimal("35.00"),
                "transmission": "Manual",
                "fuel_type": "Petrol",
                "seats": 4,
                "doors": 5,
                "luggage_capacity": 2,
                "has_air_conditioning": True,
                "has_gps": False,
                "has_bluetooth": True,
                "mileage": 31000,
                "image_url": "https://images.unsplash.com/photo-1549399542-7e3f8b79c341?auto=format&fit=crop&w=1000&q=80",
                "description": "Budget-friendly, ultra-easy to park, and extremely reliable. The ultimate solution for solo travelers and urban commutes.",
                "is_featured": False,
            },
            {
                "brand": "Range Rover",
                "model_name": "Velar R-Dynamic",
                "year": 2024,
                "category": categories["luxury"],
                "license_plate": "RR-700-VR",
                "daily_rate": Decimal("160.00"),
                "transmission": "Automatic",
                "fuel_type": "Petrol",
                "seats": 5,
                "doors": 5,
                "luggage_capacity": 4,
                "has_air_conditioning": True,
                "has_gps": True,
                "has_bluetooth": True,
                "mileage": 7500,
                "image_url": "https://images.unsplash.com/photo-1563720223185-11003d516935?auto=format&fit=crop&w=1000&q=80",
                "description": "Avant-garde luxury SUV design with flush door handles, panoramic glass roof, and supreme terrain response system.",
                "is_featured": False,
            },
            {
                "brand": "Honda",
                "model_name": "Civic Sedan",
                "year": 2023,
                "category": categories["sedan"],
                "license_plate": "HC-552-SD",
                "daily_rate": Decimal("55.00"),
                "transmission": "Automatic",
                "fuel_type": "Petrol",
                "seats": 5,
                "doors": 4,
                "luggage_capacity": 3,
                "has_air_conditioning": True,
                "has_gps": True,
                "has_bluetooth": True,
                "mileage": 18200,
                "image_url": "https://images.unsplash.com/photo-1606016159991-dfe4f2746ad5?auto=format&fit=crop&w=1000&q=80",
                "description": "Spacious family sedan with top-rated safety scores, smooth CVT transmission, and generous rear legroom.",
                "is_featured": False,
            },
        ]

        created_count = 0
        for car_dict in cars_data:
            plate = car_dict["license_plate"]
            car, created = Car.objects.update_or_create(
                license_plate=plate,
                defaults=car_dict
            )
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f"Seeded {len(cars_data)} cars ({created_count} newly created)."))

        # 5. Demo Customer Account
        customer_user, cust_created = User.objects.get_or_create(
            username="customer",
            defaults={
                "email": "customer@example.com",
                "first_name": "Alex",
                "last_name": "Rivera",
            }
        )
        if cust_created:
            customer_user.set_password("customer123")
            customer_user.save()
            profile = customer_user.customer_profile
            profile.phone = "+1 (555) 345-6789"
            profile.driver_license = "DL-ALEX-88992"
            profile.city = "Capital City"
            profile.save()
            self.stdout.write(self.style.SUCCESS("Created demo customer: username=customer, password=customer123"))

        # 6. Sample Booking for Customer
        prado = Car.objects.filter(license_plate="KDA-482M").first()
        tesla = Car.objects.filter(license_plate="EV-990-TX").first()
        airport_loc = Location.objects.first()
        downtown_loc = Location.objects.last()

        from datetime import date, timedelta
        if prado and airport_loc:
            booking, b_created = Booking.objects.get_or_create(
                booking_reference="DRV-DEMO01",
                defaults={
                    "user": customer_user,
                    "car": prado,
                    "customer_name": "Alex Rivera",
                    "customer_email": "customer@example.com",
                    "customer_phone": "+1 (555) 345-6789",
                    "customer_driver_license": "DL-ALEX-88992",
                    "pickup_location": airport_loc,
                    "return_location": downtown_loc,
                    "pickup_date": date.today() + timedelta(days=1),
                    "return_date": date.today() + timedelta(days=4),
                    "daily_rate_applied": prado.daily_rate,
                    "total_days": 3,
                    "total_amount": prado.daily_rate * 3,
                    "status": "CONFIRMED",
                    "special_requests": "Child booster seat requested.",
                }
            )
            if b_created:
                # Add sample pick-up check-out inspection
                from rentals.models import VehicleInspection
                VehicleInspection.objects.create(
                    booking=booking,
                    car=prado,
                    inspection_type="CHECK_OUT",
                    odometer_reading=prado.mileage,
                    fuel_level="FULL",
                    exterior_condition="EXCELLENT",
                    interior_condition="CLEAN",
                    has_spare_tire_and_jack=True,
                    has_all_documents=True,
                    damage_notes="No scratches or body defects found. Full tank verified.",
                    inspected_by=User.objects.filter(is_superuser=True).first()
                )
                self.stdout.write(self.style.SUCCESS("Seeded sample booking and check-out inspection."))

        # 7. Fleet Maintenance Records
        from rentals.models import MaintenanceRecord
        if prado:
            MaintenanceRecord.objects.get_or_create(
                car=prado,
                service_type="OIL_CHANGE",
                defaults={
                    "status": "COMPLETED",
                    "service_date": date.today() - timedelta(days=45),
                    "odometer_at_service": 10000,
                    "next_service_due_date": date.today() + timedelta(days=120),
                    "next_service_due_km": 20000,
                    "cost": Decimal("120.00"),
                    "service_provider": "Toyota Authorized Service Center",
                    "notes": "Full synthetic 5W-30 oil and OEM oil filter changed.",
                }
            )

        if tesla:
            MaintenanceRecord.objects.get_or_create(
                car=tesla,
                service_type="TIRE_ROTATION",
                defaults={
                    "status": "SCHEDULED",
                    "service_date": date.today() - timedelta(days=5),
                    "next_service_due_date": date.today() - timedelta(days=2),  # Overdue alert!
                    "next_service_due_km": 9000,
                    "cost": Decimal("65.00"),
                    "service_provider": "Tesla Mobile Service",
                    "notes": "Routine tire rotation and tread depth check.",
                }
            )
            self.stdout.write(self.style.SUCCESS("Seeded sample maintenance records."))

        self.stdout.write(self.style.SUCCESS("Database seeding completed successfully!"))
