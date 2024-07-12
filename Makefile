DJANGO_SETTINGS_MODULE = online_store.settings
PYTHONPATH = .

.PHONY: requirments
requirments:
	pip install -r requirments.txt

.PHONY: migrate
migrate:
	python manage.py makemigrations
	python manage.py migrate

.PHONY: superuser
superuser:
	python manage.py createsuperuser

.PHONY: runserver
runserver:
	python manage.py runserver

.PHONY: all
all: requirments migrate superuser runserver 