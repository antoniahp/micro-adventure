.PHONY: run test createmigrations migrate createsuperuser lock

run:
	docker compose up --build

test:
	docker compose run --rm app pytest

createmigrations:
	docker compose exec app python src/manage.py makemigrations

migrate:
	docker compose exec app python src/manage.py migrate


createsuperuser:
	docker compose exec app python src/manage.py createsuperuser

lock:
	poetry lock
