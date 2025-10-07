.PHONY: help install migrate test coverage lint format clean docker-build docker-up docker-down deploy

help:
	@echo "Available commands:"
	@echo "  make install       - Install dependencies"
	@echo "  make migrate       - Run database migrations"
	@echo "  make test          - Run tests"
	@echo "  make coverage      - Run tests with coverage report"
	@echo "  make lint          - Run code linting"
	@echo "  make format        - Format code"
	@echo "  make clean         - Clean up temporary files"
	@echo "  make docker-build  - Build Docker images"
	@echo "  make docker-up     - Start Docker containers"
	@echo "  make docker-down   - Stop Docker containers"
	@echo "  make collectstatic - Collect static files"
	@echo "  make superuser     - Create superuser"

install:
	pip install -r requirements.txt

migrate:
	python manage.py migrate

makemigrations:
	python manage.py makemigrations

test:
	python manage.py test --parallel

test-pytest:
	pytest -v

coverage:
	coverage run --source='.' manage.py test
	coverage report
	coverage html
	@echo "Coverage report generated in htmlcov/index.html"

lint:
	flake8 . --exclude=migrations,venv,env,.venv,__pycache__
	python manage.py check --deploy

format:
	black . --exclude="/(migrations|venv|env|\.venv|__pycache__)/"
	isort . --skip migrations --skip venv --skip env --skip .venv

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.log" -delete
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/

collectstatic:
	python manage.py collectstatic --noinput

superuser:
	python manage.py createsuperuser

runserver:
	python manage.py runserver

shell:
	python manage.py shell

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f web

docker-shell:
	docker-compose exec web python manage.py shell

docker-migrate:
	docker-compose exec web python manage.py migrate

docker-test:
	docker-compose exec web python manage.py test

deploy-check:
	python manage.py check --deploy
	python manage.py migrate --check

backup-db:
	python manage.py dumpdata --natural-foreign --natural-primary --exclude contenttypes --exclude auth.Permission > backup_$(shell date +%Y%m%d_%H%M%S).json

restore-db:
	@read -p "Enter backup file name: " file; \
	python manage.py loaddata $$file

requirements:
	pip freeze > requirements.txt
