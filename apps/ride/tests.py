from django.test import TestCase
from django.utils import timezone
from datetime import timedelta

from rest_framework.test import APIClient
from rest_framework import status

from apps.user.models import User, UserType
from apps.ride.models import Ride, RideEvent


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def create_user_type(name):
    return UserType.objects.get_or_create(name=name)[0]


def create_user(email, user_type, first_name="Test", last_name="User"):
    user = User(
        email=email,
        first_name=first_name,
        last_name=last_name,
        phone_number="09999999999",
        user_type=user_type,
    )
    user.set_password("TestPass123!")
    user.save()
    return user


def create_ride(rider, driver, status="en-route",
                pickup_lat=14.5995, pickup_lng=120.9842,
                dropoff_lat=14.6091, dropoff_lng=121.0223,
                pickup_time=None):
    return Ride.objects.create(
        status=status,
        id_rider=rider,
        id_driver=driver,
        pickup_latitude=pickup_lat,
        pickup_longitude=pickup_lng,
        dropoff_latitude=dropoff_lat,
        dropoff_longitude=dropoff_lng,
        pickup_time=pickup_time or timezone.now(),
    )


def create_ride_event(ride, description, hours_ago=0):
    return RideEvent.objects.create(
        id_ride=ride,
        description=description,
        created_at=timezone.now() - timedelta(hours=hours_ago),
    )


# ---------------------------------------------------------------------------
# Base test class — sets up users and client auth
# ---------------------------------------------------------------------------

class RideAPITestBase(TestCase):

    def setUp(self):
        self.admin_type  = create_user_type("Admin")
        self.rider_type  = create_user_type("Rider")
        self.driver_type = create_user_type("Driver")

        self.admin  = create_user("admin@test.com",  self.admin_type,  "Admin",  "User")
        self.rider  = create_user("rider@test.com",  self.rider_type,  "John",   "Rider")
        self.driver = create_user("driver@test.com", self.driver_type, "Jane",   "Driver")

        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)

        self.list_url = "/api/ride/rides/"


# ===========================================================================
# 1. QUERY COUNT TESTS  — the most important for the assessment
# ===========================================================================

class RideListQueryCountTest(RideAPITestBase):
    """
    Asserts that the Ride List API hits the database exactly 3 times:
      Query 1 — COUNT(*) for pagination
      Query 2 — SELECT rides + JOIN users (select_related)
      Query 3 — SELECT ride_events filtered to last 24h (filtered Prefetch)
    """

    def setUp(self):
        super().setUp()
        for i in range(3):
            ride = create_ride(self.rider, self.driver, pickup_lat=14.60 + i * 0.01)
            create_ride_event(ride, "Recent event", hours_ago=1)
            create_ride_event(ride, "Old event",    hours_ago=48)

    def test_list_without_coords_uses_max_3_queries(self):
        """Basic list — no GPS coords — must be exactly 3 queries."""
        with self.assertNumQueries(3):
            response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_with_distance_sorting_uses_max_3_queries(self):
        """Adding lat/lng/ordering annotates with Haversine but must NOT add extra queries."""
        with self.assertNumQueries(3):
            response = self.client.get(self.list_url, {
                "lat": "14.599812",
                "lng": "120.9884156",
                "ordering": "distance_to_pickup",
            })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_with_filters_uses_max_3_queries(self):
        """Filtering by status and rider email must not add extra queries."""
        with self.assertNumQueries(3):
            response = self.client.get(self.list_url, {
                "status": "en-route",
                "rider_email": "rider@test.com",
            })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_todays_ride_events_excludes_old_events(self):
        """todays_ride_events must only contain events from last 24h."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for ride in response.data["results"]:
            descriptions = [e["description"] for e in ride["todays_ride_events"]]
            self.assertIn("Recent event", descriptions)
            self.assertNotIn("Old event",  descriptions)

    def test_todays_ride_events_field_present_on_every_ride(self):
        """Every ride in the list must have the todays_ride_events field."""
        response = self.client.get(self.list_url)
        for ride in response.data["results"]:
            self.assertIn("todays_ride_events", ride)

    def test_rider_and_driver_nested_in_response(self):
        """Each ride must include nested rider and driver objects."""
        response = self.client.get(self.list_url)
        for ride in response.data["results"]:
            self.assertIn("id_rider",  ride)
            self.assertIn("id_driver", ride)
            self.assertIn("email", ride["id_rider"])
            self.assertIn("email", ride["id_driver"])


# ===========================================================================
# 2. AUTHENTICATION TESTS
# ===========================================================================

class AuthenticationTest(RideAPITestBase):

    def test_unauthenticated_request_returns_401(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_rider_cannot_access_api(self):
        self.client.force_authenticate(user=self.rider)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_driver_cannot_access_api(self):
        self.client.force_authenticate(user=self.driver)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_access_api(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


# ===========================================================================
# 3. FILTERING TESTS
# ===========================================================================

class RideFilterTest(RideAPITestBase):

    def setUp(self):
        super().setUp()
        self.rider2  = create_user("rider2@test.com",  self.rider_type,  "Jane", "Rider2")
        self.driver2 = create_user("driver2@test.com", self.driver_type, "Bob",  "Driver2")

        self.ride_pickup  = create_ride(self.rider,  self.driver,  status="pickup")
        self.ride_dropoff = create_ride(self.rider2, self.driver2, status="dropoff")
        self.ride_enroute = create_ride(self.rider,  self.driver2, status="en-route")

    def test_filter_by_status_pickup(self):
        response = self.client.get(self.list_url, {"status": "pickup"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for ride in response.data["results"]:
            self.assertEqual(ride["status"], "pickup")

    def test_filter_by_status_dropoff(self):
        response = self.client.get(self.list_url, {"status": "dropoff"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for ride in response.data["results"]:
            self.assertEqual(ride["status"], "dropoff")

    def test_filter_by_rider_email_exact(self):
        response = self.client.get(self.list_url, {"rider_email": "rider@test.com"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for ride in response.data["results"]:
            self.assertEqual(ride["id_rider"]["email"], "rider@test.com")

    def test_filter_by_rider_email_partial(self):
        response = self.client.get(self.list_url, {"rider_email": "rider"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data["results"]), 0)

    def test_filter_combined_status_and_email(self):
        response = self.client.get(self.list_url, {
            "status": "pickup",
            "rider_email": "rider@test.com",
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for ride in response.data["results"]:
            self.assertEqual(ride["status"], "pickup")
            self.assertEqual(ride["id_rider"]["email"], "rider@test.com")

    def test_filter_nonexistent_status_returns_empty(self):
        response = self.client.get(self.list_url, {"status": "flying"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)


# ===========================================================================
# 4. SORTING TESTS
# ===========================================================================

class RideSortingTest(RideAPITestBase):

    def setUp(self):
        super().setUp()
        now = timezone.now()
        create_ride(self.rider, self.driver, pickup_time=now - timedelta(hours=3))
        create_ride(self.rider, self.driver, pickup_time=now - timedelta(hours=2))
        create_ride(self.rider, self.driver, pickup_time=now - timedelta(hours=1))

        # Near Manila reference point
        create_ride(self.rider, self.driver, pickup_lat=14.5995, pickup_lng=120.9842)
        # Far from Manila reference point
        create_ride(self.rider, self.driver, pickup_lat=14.9999, pickup_lng=121.5000)

    def test_sort_by_pickup_time_asc(self):
        response = self.client.get(self.list_url, {"ordering": "pickup_time"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        times = [r["pickup_time"] for r in response.data["results"]]
        self.assertEqual(times, sorted(times))

    def test_sort_by_pickup_time_desc(self):
        response = self.client.get(self.list_url, {"ordering": "-pickup_time"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        times = [r["pickup_time"] for r in response.data["results"]]
        self.assertEqual(times, sorted(times, reverse=True))

    def test_sort_by_distance_asc_returns_200(self):
        response = self.client.get(self.list_url, {
            "lat": "14.599812",
            "lng": "120.9884156",
            "ordering": "distance_to_pickup",
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["results"]
        self.assertGreater(len(results), 1)
        first_lat = float(results[0]["pickup_latitude"])
        self.assertAlmostEqual(first_lat, 14.5995, places=2)

    def test_sort_by_distance_desc_returns_200(self):
        response = self.client.get(self.list_url, {
            "lat": "14.599812",
            "lng": "120.9884156",
            "ordering": "-distance_to_pickup",
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["results"]
        self.assertGreater(len(results), 1)
        first_lat = float(results[0]["pickup_latitude"])
        self.assertAlmostEqual(first_lat, 14.9999, places=2)

    def test_distance_sort_without_coords_returns_400(self):
        response = self.client.get(self.list_url, {"ordering": "distance_to_pickup"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_distance_sort_with_only_lat_returns_400(self):
        response = self.client.get(self.list_url, {
            "lat": "14.599812",
            "ordering": "distance_to_pickup",
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_default_ordering_is_pickup_time_asc(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        times = [r["pickup_time"] for r in response.data["results"]]
        self.assertEqual(times, sorted(times))


# ===========================================================================
# 5. PAGINATION TESTS
# ===========================================================================

class RidePaginationTest(RideAPITestBase):

    def setUp(self):
        super().setUp()
        for _ in range(15):
            create_ride(self.rider, self.driver)

    def test_response_has_pagination_fields(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for field in ("count", "next", "previous", "results"):
            self.assertIn(field, response.data)

    def test_page_1_and_page_2_have_no_overlap(self):
        r1 = self.client.get(self.list_url, {"page": 1})
        r2 = self.client.get(self.list_url, {"page": 2})
        ids_p1 = {r["id_ride"] for r in r1.data["results"]}
        ids_p2 = {r["id_ride"] for r in r2.data["results"]}
        self.assertEqual(ids_p1 & ids_p2, set())

    def test_distance_sort_pagination_no_overlap(self):
        params = {
            "lat": "14.599812",
            "lng": "120.9884156",
            "ordering": "distance_to_pickup",
        }
        r1 = self.client.get(self.list_url, {**params, "page": 1})
        r2 = self.client.get(self.list_url, {**params, "page": 2})
        self.assertEqual(r1.status_code, status.HTTP_200_OK)
        self.assertEqual(r2.status_code, status.HTTP_200_OK)
        ids_p1 = {r["id_ride"] for r in r1.data["results"]}
        ids_p2 = {r["id_ride"] for r in r2.data["results"]}
        self.assertEqual(ids_p1 & ids_p2, set())


# ===========================================================================
# 6. CRUD TESTS
# ===========================================================================

class RideCRUDTest(RideAPITestBase):

    def setUp(self):
        super().setUp()
        self.ride = create_ride(self.rider, self.driver)

    def _payload(self, **overrides):
        base = {
            "status": "en-route",
            "pickup_latitude": 14.5995,
            "pickup_longitude": 120.9842,
            "dropoff_latitude": 14.6091,
            "dropoff_longitude": 121.0223,
            "pickup_time": timezone.now().isoformat(),
            "id_rider_id": self.rider.id,
            "id_driver_id": self.driver.id,
            "ride_events": [],
        }
        base.update(overrides)
        return base

    def test_create_ride_returns_201(self):
        response = self.client.post(self.list_url, self._payload(), format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["message"], "Ride created successfully.")

    def test_create_ride_wrong_user_type_returns_400(self):
        """Assigning a rider as the driver must fail validation."""
        response = self.client.post(
            self.list_url,
            self._payload(id_driver_id=self.rider.id),
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_ride(self):
        response = self.client.get(f"{self.list_url}{self.ride.id_ride}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id_ride"], self.ride.id_ride)

    def test_partial_update_status(self):
        response = self.client.patch(
            f"{self.list_url}{self.ride.id_ride}/",
            {"status": "pickup"},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.ride.refresh_from_db()
        self.assertEqual(self.ride.status, "pickup")

    def test_delete_ride(self):
        response = self.client.delete(f"{self.list_url}{self.ride.id_ride}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Ride.objects.filter(id_ride=self.ride.id_ride).exists())
