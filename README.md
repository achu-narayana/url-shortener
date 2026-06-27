# URL Shortener 🔗

A high-performance, resilient URL shortening service built with **FastAPI**, **PostgreSQL**, and **Redis**. Designed with a modern, glassmorphic dark-theme frontend client and robust backend caching strategies.

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis)](https://redis.io/)
[![Vercel](https://img.shields.io/badge/Vercel-000000?style=for-the-badge&logo=vercel)](https://vercel.com/)
[![Render](https://img.shields.io/badge/Render-46E3B7?style=for-the-badge&logo=render)](https://render.com/)

---

## 🚀 Live Demo

Experience the application live in production:

*   **Frontend Client:** [https://url-shortener-lime-gamma.vercel.app](https://url-shortener-lime-gamma.vercel.app)
*   **Backend API Base:** [https://url-shortener-es94.onrender.com](https://url-shortener-es94.onrender.com)
*   **Interactive Swagger Documentation:** [https://url-shortener-es94.onrender.com/docs](https://url-shortener-es94.onrender.com/docs)

---

## 📌 Problem Statement

In today's digital landscape, links are the primary medium of exchange. However, long, complex URLs containing tracking tokens and query parameters are difficult to share, look unprofessional, and break easily in messaging formats.

A custom URL shortener addresses these challenges by transforming long links into concise, memorable URLs. This is particularly useful for:
*   **Social Media & Marketing:** Optimizing character limits on platforms like Twitter and creating clean ad campaigns.
*   **Social & Communication Channels:** Clean URLs for email newsletters, QR codes, SMS, and event registrations.
*   **Analytics & Insights:** Tracking click rates and user engagement metrics in real-time.

---

## ✨ Features

*   **URL Shortening:** Generate clean, unique, short codes for long destination URLs.
*   **High-Speed Redirection:** Fast 302 redirects served with optimal response times.
*   **Redis Caching:** Minimizes database read latency by caching shortened URLs.
*   **Resilient Fallback Design:** Gracefully bypasses cache layers and query PostgreSQL directly if Redis is offline.
*   **Interactive API Docs:** Built-in Swagger UI for testing API endpoints out of the box.
*   **Analytics Tracking:** Monitor click counts and timestamps for each shortened URL.
*   **Responsive UI:** Glassmorphism-inspired dark-theme client optimized for desktop and mobile viewports.

---

## 🛠️ Tech Stack

*   **Backend:** Python 3.13, FastAPI, SQLAlchemy (Async), Pydantic v2, Alembic
*   **Frontend:** Vanilla HTML5, CSS3 (Glassmorphism UI), ES6 JavaScript
*   **Database:** PostgreSQL 18
*   **Cache:** Redis 5.0 (with async fallback)
*   **Deployment:** Vercel (Frontend), Render (Backend, PostgreSQL, Redis)

---

## 📐 System Architecture

The following diagram illustrates the flow of requests from the client down to the database:

![System Architecture](assets/system_architecture.png)

```mermaid
graph TD
    User([User Client])
    Frontend[Vercel Frontend]
    Backend[Render FastAPI Backend]
    Cache[(Redis Cache)]
    DB[(PostgreSQL Database)]

    User -->|Interacts with| Frontend
    Frontend -->|API Requests| Backend
    Backend -->|1. Check Cache| Cache
    Backend -->|2. Fallback / Persist| DB
```

---

## 🖼️ Application Screenshots

### 1. Home Page (Initial State)
![Home Page Initial State](assets/home_page_empty.png)
*Initial clean, responsive user interface featuring glassmorphic dark-theme elements.*

### 2. URL Successfully Shortened
![URL Successfully Shortened](assets/url_shortened_and_history.png)
*Displays the shortened URL prominently with a dynamic copy-to-clipboard action.*

### 3. Recent Links (Session History)
![Recent Links](assets/url_shortened_and_history.png)
*Maintains a session list of recently shortened links, featuring individual Copy and Analytics lookup hooks.*

### 4. Live Analytics
![Analytics Results](assets/url_shortened_and_history.png)
*Detailed statistics displaying total click counts, short codes, creation timestamps, and target long URLs.*

### 5. Swagger Documentation
![Swagger API Documentation](assets/swagger_documentation.png)
*Interactive OpenAPI documentation showing API endpoint definitions and model schemas.*

---

## 💡 Real-World Example

Here is how the application works end-to-end to solve link sharing complexity:

1.  **Original URL:** (A lengthy AWS event registration URL)
    ```text
    https://aws.amazon.com/events/reinvent/experiences/all-builders-welcome/?mcp_token=eyJwaWQiOjE0MTkzMTIsInNpZCI6MTYxMzE5MjkyMywiYXgiOiI0MDAxN2Q3MjY1ZDc4ZjFlOTVjMWYyNzllODQxNTE5YyIsInRzIjoxNzgyNDYwMTQ2LCJleHAiOjE3ODQ4NzkzNDZ9.CWZMjaQTpAGzjSLRFF1SUp8yDpXwj5C_6a9Qo28TinY&fbclid=PAT01DUASrDldleHRuA2FlbQIxMABzcnRjBmFwcF9pZA81NjcwNjczNDMzNTI0MjcAAadTzWomGjshCw-EDe5gv0KzYevaOmCCckikHxRWaeS2977wJHVIpQKQ8gCl1Q_aem_lyx_R0OVEER4-z6Yjq08PQ
    ```
2.  **Shortened URL:**
    ```text
    https://url-shortener-es94.onrender.com/0000001
    ```
3.  **Flow:**
    *   The user shares the shortened link.
    *   A visitor opens the shortened URL and is instantly redirected to the AWS page.
    *   The database and analytics logs record the visit, incrementing the click counter.

---

## 🔌 API Endpoints

| Method | Endpoint | Description | Response Code |
| :--- | :--- | :--- | :--- |
| **POST** | `/shorten` | Shortens a target URL. Accepts optional expiration parameters. | `201 Created` |
| **GET** | `/{short_code}` | Resolves the short code and redirects to the original destination URL. | `302 Found` |
| **GET** | `/analytics/{short_code}` | Retrieves click statistics and metadata for a short code. | `200 OK` |
| **DELETE** | `/{short_code}` | Deletes a short code from the system. | `204 No Content` |

---

## 📂 Folder Structure

```text
.
├── alembic/             # Database migration history and env scripts
├── app/                 # Core backend API application
│   ├── api/             # FastAPI routers and endpoints
│   ├── core/            # Config parsing and db connection pools
│   ├── db/              # Database drivers (Redis/Postgres client)
│   ├── models/          # SQL database schemas
│   ├── schemas/         # Pydantic data schemas
│   └── services/        # URL hashing and cache operations
├── assets/              # High-quality README screenshots
├── frontend/            # HTML/CSS/JS frontend files
└── tests/               # Backend route and business logic tests
```

---

## 💻 Running Locally

### 1. Environment Configurations
Create a `.env` file in the project root:
```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/url_shortener
REDIS_URL=redis://localhost:6379/0
SHORT_CODE_LENGTH=7
BASE_URL=http://localhost:8000
FRONTEND_URL=http://localhost:5500
CACHE_TTL_SECONDS=3600
```

### 2. Setup Database & Cache Services
Ensure local PostgreSQL and Redis instances are running locally on their default ports.

### 3. Initialize Virtual Environment & Packages
```bash
python -m venv .venv
# On Windows PowerShell:
.venv\Scripts\Activate.ps1
# Install dependencies:
pip install -r requirements.txt
```

### 4. Run Migrations & Start Servers
```bash
# Run database migrations
alembic upgrade head

# Start backend server
uvicorn app.main:app --reload

# Start local frontend server (from the frontend directory)
cd frontend
python -m http.server 5500
```
Open `http://localhost:5500` in your web browser.

---

## 🔮 Future Improvements

*   **User Authentication:** User accounts, dashboard logins, and private URL history.
*   **Custom Short URL Aliases:** Let users specify their own custom text for short codes.
*   **QR Code Generation:** Share shortened links as QR codes natively.
*   **API Rate Limiting:** Prevent request floods on the shorten endpoints.
*   **Automated URL Expiration:** Automatic scheduled deletions of inactive links.
*   **Containerization & DevOps:** Dockerization and CI/CD workflows for deployments.

---

## ✍️ Author

**Surawi Archana Reddy**
*   **GitHub:** [@achu-narayana](https://github.com/achu-narayana)
*   **LinkedIn:** [https://www.linkedin.com/in/surawi-archana-4219a6344/)
