# PR Analytics Dashboard

pulls pull request and review data from the github API for a chosen repo, stores it in Postgres, and shows metrics through a small dashboard

![CI](https://github.com/ConnorMB/pr-dashboard/actions/workflows/ci.yml/badge.svg)

**Live demo:** https://pr-dashboard-1.onrender.com

## Stack

- FastAPISQLAlchemy, Postgres (Neon in production), React + Vite, recharts, Docker(local dev only), GitHub Actions (CI), Render (deployment)

## Run locally

\`\`\`bash
cp .env.example .env   # fill in GITHUB_REPO and GITHUB_TOKEN
docker compose up --build
\`\`\`
frontend -> http://localhost:5173

## Tests

\`\`\`bash
cd backend && python -m pytest -v
\`\`\`

## notes

so slow need to fix
