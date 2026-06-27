# URL Shortener

A high-performance URL shortening service built with FastAPI, PostgreSQL, and Redis.

## Running locally

Follow these steps to set up and run the service locally:

### 1. Environment Setup

Create a `.env` file in the root directory based on the `.env.example` file. Make sure the following keys are set:

- `DATABASE_URL` should point to your PostgreSQL database (using the `asyncpg` driver):
  ```env
  DATABASE_URL=postgresql+asyncpg://<user>:<password>@localhost:5432/url_shortener_db
  ```
- `REDIS_URL` should point to your Redis instance:
  ```env
  REDIS_URL=redis://localhost:6379/0
  ```

### 2. Activate the virtual environment

Depending on your operating system and shell, run one of the following commands:

- **Windows (PowerShell)**:
  ```powershell
  .venv\Scripts\Activate.ps1
  ```
- **Windows (CMD)**:
  ```cmd
  .venv\Scripts\activate.bat
  ```
- **macOS / Linux**:
  ```bash
  source .venv/bin/activate
  ```

### 3. Install dependencies

Install the project dependencies from `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 4. Apply migrations

Run Alembic migrations to set up the database tables:

```bash
alembic upgrade head
```

### 5. Start the API

Run the FastAPI development server with reload enabled:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API documentation will be available at `http://localhost:8000/docs`.

## Running the frontend

Since this is plain HTML/CSS/JS with no build step, it can't just be opened directly as a file:// URL because fetch() calls to the backend may be blocked depending on browser security settings for local files — instead, serve it with a simple local server. From inside the frontend folder, run:

```bash
python -m http.server 5500
```

Then open `http://localhost:5500` in the browser. Note that the backend (uvicorn) must already be running on port 8000, and Postgres/Redis must be running too, before testing the frontend.

