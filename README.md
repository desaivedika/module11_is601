# FastAPI Calculator with Secure Users and Calculation Model

A FastAPI application that stores users and their calculations in PostgreSQL using SQLAlchemy, with validation by Pydantic. Users have bcrypt-hashed passwords. Each calculation (Add, Sub, Multiply, Divide) belongs to a user, and its result is computed by a factory. Every push to `main` runs all tests in GitHub Actions against a real PostgreSQL database, scans the Docker image with Trivy, and publishes it to Docker Hub.

**Docker Hub repository:** https://hub.docker.com/r/desaiveds/module11_is601

## Calculation Model (Module 11)

- **SQLAlchemy `Calculation` model** (`app/models/calculation.py`): `id`, `a`, `b`, `type`, `result`, `user_id` and `created_at`.
  - The result is **stored**: it is computed once when the calculation is saved.
  - `user_id` is a **foreign key** to `users.id` with `ON DELETE CASCADE`, so deleting a user deletes their calculations.
  - Database **check constraints** reject unknown types and division by zero, even if application validation were bypassed.
- **Pydantic schemas** (`app/schemas/calculation.py`):
  - `CalculationCreate` takes `a`, `b` and `type`. The type must be Add, Sub, Multiply or Divide (any letter case). It rejects a zero divisor for Divide, and rejects text, infinity or NaN as operands.
  - `CalculationRead` returns `id`, `a`, `b`, `type`, `result`, `user_id` and `created_at`, with no user details.
- **Factory pattern** (`app/calculation_factory.py`): `CalculationFactory.create(type)` returns the right operation class (`AddOperation`, `SubOperation`, `MultiplyOperation` or `DivideOperation`). Adding a new type only needs one new class and one registry entry.
- **Data functions** (`app/crud.py`): `create_calculation`, `get_calculation` and `list_calculations_for_user`. The API routes for calculations come in Module 12.

## User Model (Module 10)

- `User` model with a unique `username`, a unique `email`, `password_hash` and `created_at`.
- `UserCreate` and `UserRead` schemas. Passwords are hashed with bcrypt in `app/security.py`.
- `POST /users/register` and `GET /users/{id}`, plus the calculator page at `/`.

## Running Tests Locally

1. Create a virtual environment and install the dependencies:
   ~~~bash
   python -m venv venv
   source venv/Scripts/activate     # Windows (Git Bash)
   # source venv/bin/activate       # macOS / Linux
   pip install -r requirements.txt
   ~~~

2. Start PostgreSQL. Integration tests need a real database:
   ~~~bash
   docker compose up -d db
   ~~~

3. Run the tests:
   ~~~bash
   # All tests, with coverage
   pytest --cov=app --cov=main --cov-report=term-missing

   # Only the new calculation tests
   pytest tests/unit/test_calculation_factory.py tests/unit/test_calculation_schemas.py
   pytest tests/integration/test_calculation_model.py

   # By type
   pytest tests/unit          # unit tests (no database needed)
   pytest tests/integration   # integration tests (PostgreSQL)
   ~~~
   The tests connect using `DATABASE_URL`, which defaults to `postgresql://postgres:postgres@localhost:5432/fastapi_db`. To use a different database, copy `.env.example` to `.env` and edit it.

   > **Warning:** the integration tests empty the `users` and `calculations` tables, so don't point `DATABASE_URL` at data you want to keep.

4. Stop the database when you're done: `docker compose down`

## Running the Application

~~~bash
docker compose up --build
~~~
- App: http://localhost:8000
- API docs: http://localhost:8000/docs
- pgAdmin: http://localhost:5050 (login `admin@example.com` / `admin`; database host `db`, user `postgres`, password `postgres`)

From Docker Hub:
~~~bash
docker pull desaiveds/module11_is601:latest
docker run -p 8000:8000 desaiveds/module11_is601:latest
~~~

## CI/CD Pipeline

`.github/workflows/ci-cd.yml` runs on every push and pull request to `main`:

1. **test:** starts a PostgreSQL 16 service container and runs all unit and integration tests (users and calculations). It fails if coverage drops below 90%.
2. **security:** builds the Docker image and scans it with Trivy.
3. **deploy:** runs on pushes to `main` after the first two jobs pass. It pushes `desaiveds/module11_is601:latest` and `desaiveds/module11_is601:<commit-sha>` to Docker Hub.

The deploy job uses two repository secrets: `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN`.
