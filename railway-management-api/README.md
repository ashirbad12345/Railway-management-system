# Railway Management API

Django REST API for railway management using Django REST Framework, MySQL, JWT authentication, and an API key for admin operations.

## Features

- User registration and JWT login
- Admin train creation and capacity updates protected by `X-API-Key`
- Train search by source and destination
- Live seat availability
- Transaction-safe booking with MySQL row locking
- User-owned booking history and details
- Separate user and admin dashboards

## Requirements

- Python 3.10 or later
- MySQL 8 or later, or Docker Desktop
- PowerShell on Windows

## Setup From Scratch

### 1. Get the project

```powershell
cd D:\
git clone <repository-url> railway-management-api
cd D:\railway-management-api
```

If the project is already present, only run:

```powershell
cd D:\railway-management-api
```

### 2. Create the Python environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Create the MySQL database

Start MySQL Server. If it is installed as MySQL80, use an Administrator PowerShell:

```powershell
Start-Service MYSQL80
```

Alternatively, with Docker Desktop running:

```powershell
docker compose up -d mysql
```

For MySQL Workbench, connect to `127.0.0.1:3306` with an administrator account and run:

```sql
CREATE DATABASE IF NOT EXISTS railway_management
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'railway'@'localhost'
  IDENTIFIED BY 'railway';

ALTER USER 'railway'@'localhost' IDENTIFIED BY 'railway';
GRANT ALL PRIVILEGES ON railway_management.* TO 'railway'@'localhost';
FLUSH PRIVILEGES;
```

The application database settings are:

```text
Host: 127.0.0.1
Port: 3306
Database: railway_management
User: railway
Password: railway
```

### 4. Configure environment variables

```powershell
Copy-Item .env.example .env
```

Edit `.env`:

```env
DJANGO_SECRET_KEY=replace-with-a-long-random-secret
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
MYSQL_DATABASE=railway_management
MYSQL_USER=railway
MYSQL_PASSWORD=railway
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
ADMIN_API_KEY=replace-with-a-long-random-admin-key
```

Generate a secret with:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Never commit `.env`. It is ignored by `.gitignore`.

### 5. Create tables and sample trains

```powershell
python manage.py migrate
python manage.py seed_demo_trains
```

The sample command creates these train options in MySQL and is safe to run repeatedly:

```text
12951 Rajdhani Express     Delhi      -> Mumbai
12011 Shatabdi Express     Delhi      -> Chandigarh
12123 Deccan Queen         Mumbai     -> Pune
12841 Coromandel Express   Kolkata    -> Chennai
20607 Vande Bharat         Bengaluru  -> Chennai
```

### 6. Run the project

```powershell
python manage.py runserver 127.0.0.1:8000
```

User dashboard:

```text
http://127.0.0.1:8000/
```

Admin dashboard:

```text
http://127.0.0.1:8000/admin-dashboard/
```

Django admin:

```text
http://127.0.0.1:8000/admin/
```

Create a Django admin user if needed:

```powershell
python manage.py createsuperuser
```

## User Flow

1. Open the user dashboard.
2. Register with a username and password of at least eight characters.
3. Sign in to receive JWT access and refresh tokens.
4. Select a train from the database-backed dropdown or search by route.
5. Click **Book seat** and enter a number such as `1`.
6. View the saved booking in **Your bookings**.

## Admin Flow

1. Open `/admin-dashboard/`.
2. Enter the value of `ADMIN_API_KEY` from `.env`.
3. Enter a unique train number, name, source, destination, and total seats.
4. Click **Add train**.

The train is stored in MySQL and appears in the user dashboard after refresh.

## API Endpoints

Base URL:

```text
http://127.0.0.1:8000/api/
```

| Method | Endpoint | Authentication | Purpose |
| --- | --- | --- | --- |
| POST | `/auth/register/` | None | Register a user |
| POST | `/auth/login/` | None | Return JWT access and refresh tokens |
| POST | `/auth/refresh/` | Refresh token | Refresh an access token |
| GET | `/trains/?source=Delhi&destination=Mumbai` | None | Search trains and availability |
| GET | `/trains/catalog/` | None | List all trains |
| POST | `/admin/trains/` | `X-API-Key` | Add a train |
| PATCH/PUT | `/admin/trains/<id>/` | `X-API-Key` | Update train capacity or details |
| POST | `/trains/<id>/bookings/` | `Bearer <access>` | Book seats |
| GET | `/bookings/` | `Bearer <access>` | List the current user's bookings |
| GET | `/bookings/<id>/` | `Bearer <access>` | Get an owned booking |

Admin train request:

```json
{
  "train_number": "12801",
  "name": "Morning Express",
  "source": "Delhi",
  "destination": "Mumbai",
  "total_seats": 100
}
```

Booking request:

```json
{
  "seats": 1
}
```

Authenticated requests use:

```http
Authorization: Bearer <access-token>
```

Admin requests use:

```http
X-API-Key: <ADMIN_API_KEY>
```

## Booking Concurrency

Booking is performed inside `transaction.atomic()` and locks the selected train row with `select_for_update()`. If two users request the last seat concurrently, one transaction succeeds and the other receives HTTP `409`; availability never becomes negative.

Users can only access their own bookings. Passwords are hashed by Django and are never stored as plain text.

The project assumes a train is a direct source-to-destination route. Intermediate stations and per-segment inventory are outside this assignment's scope.

## Tests

Run:

```powershell
python manage.py test
```

Django creates a temporary MySQL database named `test_railway_management`. The MySQL user needs permission to create and drop it. Run this once in MySQL Workbench as an administrator:

```sql
GRANT CREATE, DROP ON *.* TO 'railway'@'localhost';
GRANT ALL PRIVILEGES ON railway_management.* TO 'railway'@'localhost';
FLUSH PRIVILEGES;
```

The tests cover registration/login, train search, successful booking, insufficient availability, and booking ownership.

## Troubleshooting

### MySQL connection refused

Verify MySQL is running and port `3306` is open:

```powershell
Test-NetConnection 127.0.0.1 -Port 3306
```

### Invalid JWT token

Clear old browser tokens and sign in again:

```javascript
localStorage.removeItem("railway_access");
localStorage.removeItem("railway_refresh");
location.reload();
```

### Admin returns `403`

Make sure the key entered in the admin dashboard exactly matches `ADMIN_API_KEY` in `.env`, then restart Django.

### Empty train dropdown

Run:

```powershell
python manage.py seed_demo_trains
```

Then refresh the dashboard with `Ctrl+F5`.
