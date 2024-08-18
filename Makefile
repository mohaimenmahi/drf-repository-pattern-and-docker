build:
	docker compose build

up:
	docker compose up

down:
	docker compose down

dev: down up log

log:
	docker logs --follow big-api

enter:
	docker exec -it big-api sh

enter-db:
	docker exec -it big-db psql -U postgres

install-deps:
	pip3 install -r requirements.txt

create-migrations:
	python3 manage.py makemigrations

run-migrations:
	python3 manage.py migrate