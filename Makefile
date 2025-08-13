run:
	python cmd/main.py

build: Dockerfile
	docker build -t spending_tracker_image .

test: tests
	pytest

lint:
	ruff check

migrate:
	alembic upgrade head

fix-imports:
	ruff check --select I --fix