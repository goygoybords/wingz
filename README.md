
# Wingz API — Django Backend Developer Assessment

A Django REST Framework API for managing ride, user, and ride event data with performance-optimized listing, filtering, sorting, and authentication.

---

## Objective

This project is part of the Django Backend Developer Test. It demonstrates:

- Django REST Framework usage
- Admin-only role-based API access
- CRUD support for `User`, `Ride`, and `RideEvent`
- Filtering and pagination
- Haversine-based distance sorting
- Performance-conscious querying

---

## Requirements

- Python 3.12+
- PostgreSQL
- pip (or pipenv)
- `virtualenv` recommended

---

## Installation (No Docker)

1. **Clone the repository**

```bash
git clone https://github.com/goygoybords/wingz-exam.git
cd wingz-exam
```

2. **Create a virtual environment**

```bash
python -m venv wingzvenv  # or python3
```

3. **Activate the virtual environment and install dependencies**

```bash
source wingzvenv/bin/activate  # On Windows: wingzvenv\Scripts\activate
pip install -r requirements.txt
```

4. **Rename `.env-example` to `.env`**

```bash
cp .env-example .env
```

Then open `.env` and update your configuration.

5. **Apply database migrations**

```bash
python manage.py migrate
```

6. **Run the seeder files to seed data**

```bash
python manage.py seed_usertypes

python manage.py seed_admin_user

python manage.py seed_riders_drivers

python manage.py seed_rides
```

7. **Run the development server**

```bash
python manage.py runserver
```

---

## 🐳 Docker Setup

This project includes a full Docker environment with PostgreSQL for local development.

### Prerequisites

- Docker Engine
- Docker Compose v2

### Steps

1. **Copy and configure your environment file**

```bash
cp .env-example .env
```

Update `.env` values as needed (e.g., `SECRET_KEY`, `DEBUG`, DB credentials).

2. **Build and run the containers**

```bash
docker compose up --build
```

This will:

- Build the Django app image
- Start PostgreSQL 16
- Apply DB migrations
- Seed user types, admin user, drivers and riders, rides and ride events
- Launch the dev server at [http://localhost:8000](http://localhost:8000)

3. **Stop the containers**

```bash
docker compose down
```

To stop and remove containers and volumes:

```bash
docker compose down -v
```

---

## Testing

You can test the API using the provided Postman collection and environment files.

### 🧪 Requirements

- [Download and install Postman](https://www.postman.com/downloads/)

---

### 📬 Postman Setup

1. Open Postman and import the following files from the `postman-collections/` folder:

   - **Collection:**  
     `postman-collections/Wingz.postman_collection.json`

   - **Environment:**  
     `postman-collections/Wingz.postman_environment.json`

2. In Postman, select the imported environment (`Wingz`) from the top-right dropdown.

3. Use the **Login** request to authenticate. It will automatically save the JWT access and refresh tokens as environment variables.

4. All authorized requests (e.g., User, Ride, RideEvent APIs) will use the saved `{{access_token}}` for the `Authorization` header.


## 🧩 Bonus Question - SQL Report Task

For reporting purposes, we need a raw SQL statement (included below), which returns the count of Trips that took more than 1 hour from Pickup to Dropoff. The output should be grouped by **Month** and **Driver**.

### 📄 Sample Report

| Month    | Driver     | Count of Trips > 1 hr |
|----------|------------|------------------------|
| 2024-01  | Chris H    | 4                      |
| 2024-01  | Howard Y   | 5                      |
| 2024-01  | Randy W    | 2                      |
| 2024-02  | Chris H    | 7                      |
| 2024-02  | Howard Y   | 5                      |
| 2024-03  | Chris H    | 2                      |
| 2024-03  | Howard Y   | 2                      |
| 2024-03  | Randy W    | 11                     |
| 2024-04  | Howard Y   | 7                      |
| 2024-04  | Randy W    | 3                      |

When a driver picks up a rider, a `RideEvent` will be created with the description `'Status changed to pickup'`, and similarly, when a rider is dropped off, a `RideEvent` will be created with the description `'Status changed to dropoff'`.

To calculate the duration of the trip, the system must locate the pickup and dropoff `RideEvent`s for each ride and compute the time difference.

> 📝 **Note:** You do **not** need to implement the logic that populates the `RideEvent` table. You may assume it is already populated for the purpose of this query.

Ideally, in a real-world scenario, the distance and duration would be stored directly on the `Ride` model. However, for this assessment, the `Ride` table structure **must not be changed**.

## 📊 SQL Report: Count of Trips > 1 Hour (by Month and Driver) - Answer to Bonus Question

The following raw SQL query returns the number of trips that took more than 1 hour, grouped by driver and by month:

```sql
WITH dropoff_events AS (
    SELECT id_ride_id, MAX(created_at) AS dropoff_time
    FROM ride_rideevent
    WHERE description ILIKE 'Status changed to dropoff'
    GROUP BY id_ride_id
),
ride_durations AS (
    SELECT
        r.id_ride,
        r.id_driver_id,
        r.pickup_time,
        de.dropoff_time,
        (de.dropoff_time - r.pickup_time) AS duration
    FROM dropoff_events de
    JOIN ride_ride r ON r.id_ride = de.id_ride_id
    WHERE (de.dropoff_time - r.pickup_time) > INTERVAL '1 hour'
)
SELECT
    TO_CHAR(rd.pickup_time, 'YYYY-MM') AS month,
    uu.first_name || ' ' || uu.last_name AS driver,
    COUNT(*) AS "Count of Trips > 1 hr"
FROM ride_durations rd
JOIN user_user uu ON uu.id = rd.id_driver_id
GROUP BY month, driver
ORDER BY month, driver;
```

## 📝 Note: The seeded data is a set of randomized test entries designed to ensure this query can be executed and return meaningful results, including trips longer than 1 hour.


## 📊 Additional Notes

    UserType Model for Role Management:
     - To make handling user roles easier, I created a separate UserType model. In best practice it is always good to create a table for user types or roles.

    Authentication and Permissions:
     - Created a custom permission class IsAdminUser. Although while this was not fully enforced in the API since we are assuming only admin will be consuming it for now, this approach reflects best practices in terms of permission control.
     