
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
- Seed user types and admin user
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