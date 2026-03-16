# Zoho Support Copilot (Bootstrap)

Runnable monorepo for a demo-ready, mocked Zoho Support Copilot MVP.

## Stack

- `apps/web`: Next.js 14 + TypeScript + Tailwind
- `apps/api`: FastAPI + Python
- `packages/shared`: shared TypeScript and Python API contracts

## Prerequisites

- Node.js 20+
- Python 3.10+

## Setup

1. Install JavaScript dependencies from the repo root:

   ```bash
   npm install
   ```

2. Bootstrap backend dependencies (works well in CodeSandbox too):

   ```bash
   npm run setup:api
   ```

   Or run manually:

   ```bash
   cd apps/api
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   cd ../..
   ```

## Run locally

From the repo root:

```bash
npm run dev
```

This starts:

- Web app: `http://localhost:3000`
- API: `http://localhost:8000`

Set `NEXT_PUBLIC_API_BASE_URL` if the API is not on `http://localhost:8000`.

## MVP workflows

- **Ask**: returns grounded answers with official Zoho sources and trust labels.
- **Similar Tickets**: returns historical ticket matches with similarity scores and draft replies.
- **Live Assist**: safe placeholder UI (intentionally non-functional in MVP).

## API endpoints

- `GET /health`
- `POST /api/answer`
- `POST /api/similar-tickets`
- `POST /api/tickets/search`
- `GET /api/tickets/{ticket_id}`

## Testing

Run everything from the repo root:

```bash
npm test
```

Or run each suite independently:

```bash
npm run test:web
npm run test:api
```

> `npm run test:api` now auto-creates `apps/api/.venv` and installs `requirements.txt` if needed, which prevents `No module named pytest` errors in fresh environments.
