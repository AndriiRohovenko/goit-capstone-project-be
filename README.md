# GoIt PythonWeb HW-10

A REST API project built with **FastAPI**, **PostgreSQL**, and **Docker Compose**, managed using **Poetry**.

## 🚀 Features

- ✅ Asynchronous API with FastAPI
- ✅ PostgreSQL database integration
- ✅ Alembic migrations for database versioning
- ✅ Async SQLAlchemy ORM
- ✅ User management (CRUD operations, search, upcoming birthdays)
- ✅ Email verification using FastAPI-Mail
- ✅ Background tasks for email sending
- ✅ Cloud image uploading (new feature)
- ✅ Custom error handling
- ✅ Token-based authentication (JWT)
- ✅ Dockerized for easy deployment

---

## 📦 Requirements

- Python 3.11+
- Poetry
- Docker & Docker Compose

---

## ⚙️ Environment Variables

Create a `.env` file in the root directory with the following content:

```env
# Database Configuration
DB_HOST=db
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=postgres

# API Configuration
API_HOST=0.0.0.0
API_PORT=5000

# SMTP Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=465
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_password
SMTP_FROM=your_email@gmail.com

# JWT Configuration
JWT_SECRET=your_jwt_secret
JWT_ALGORITHM=HS256
JWT_EXPIRATION_SECONDS=3600

CLOUDINARY_NAME=your_name_key
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

APP_ENV=prod OR dev
! Possible to setup dev and prod env by creating two files .env and .env.dev in project root

```

🛠️ Project Structure
src/api: API routes and endpoints
src/conf: Configuration files
src/db: Database models and Alembic migrations
src/repository: Data access layer
src/schemas: Pydantic models for request/response validation
src/services: Business logic (authentication, email, file uploads, etc.)
src/templates: HTML templates for email content

🚀 Run with Docker
To build and start the app with Docker Compose:

```
docker compose up -d --build
```

💻 Run Locally with Poetry

1. Install dependencies:

```
poetry install
```

2. Run PostgreSQL database locally or in docker.
3. Set up the .env.dev file.
   4.Start the development server (with auto-reload):

```
poetry run dev
```

📬 Email Verification
The project uses FastAPI-Mail for sending email verification links.
Email templates are located in the src/templates directory.

📤 Cloud Image Uploading
The project supports uploading images to the cloud.
Ensure the cloud storage credentials are configured in the .env file.

🛠️ Alembic Migrations
Generate a new migration:

```
poetry run alembic revision --autogenerate -m "Migration message"
```

2. Apply migrations

```
poetry run alembic upgrade head
```
