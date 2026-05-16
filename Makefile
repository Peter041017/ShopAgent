.PHONY: install dev-up dev-down index run test lint init-db frontend db-clean

install:
	pip install -e ".[dev]"
	cd frontend && npm install

dev-up:
	docker compose up -d

dev-down:
	docker compose down

init-db:
	python scripts/init_db.py

db-clean:
	rm -f data/shopagent.db

index:
	python scripts/build_index.py

run:
	uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

frontend:
	cd frontend && npm run dev

test:
	pytest tests -q --asyncio-mode=auto -W ignore::UserWarning

lint:
	ruff check src tests scripts
