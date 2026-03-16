# Zoho Support Copilot (Bootstrap)

Initial runnable monorepo for a mocked Zoho Support Copilot.

## Stack

- `apps/web`: Next.js 14 + TypeScript + Tailwind
- `apps/api`: FastAPI + Python
- `packages/shared`: shared TypeScript types/schemas

## Prerequisites

- Node.js 20+
- Python 3.11+

## Setup

1. Install JavaScript dependencies:
   ```bash
   npm install
   ```

2. Install backend dependencies:
   ```bash
   cd apps/api
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   cd ../..
   ```

## Run locally

From repo root:

```bash
npm run dev
```

This starts:
- Web app: `http://localhost:3000`
- API: `http://localhost:8000`

Set `NEXT_PUBLIC_API_BASE_URL` if the API is not on `http://localhost:8000`.

## Available views

- Ask
- Similar Tickets
- Live Assist (placeholder UI)

## API endpoints

- `GET /health`
- `POST /api/answer`
- `POST /api/similar-tickets`

## Testing

Run all tests:

```bash
npm test
```

Or separately:

```bash
npm run test:web
npm run test:api
```
