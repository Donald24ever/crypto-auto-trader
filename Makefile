.PHONY: setup backend frontend test lint typecheck clean

setup:
	cd backend && python -m venv .venv && ./.venv/bin/pip install -e ".[dev]"
	cd frontend && npm install

backend:
	cd backend && ./.venv/bin/uvicorn app.main:app --reload --port 8000

frontend:
	cd frontend && npm run dev

test:
	cd backend && ./.venv/bin/pytest -q

lint:
	cd backend && ./.venv/bin/ruff check .
	cd frontend && npm run lint

typecheck:
	cd frontend && npm run typecheck

build-frontend:
	cd frontend && npm run build

clean:
	rm -rf backend/.venv backend/auto_trader.db backend/.pytest_cache backend/.ruff_cache
	rm -rf frontend/node_modules frontend/.next
