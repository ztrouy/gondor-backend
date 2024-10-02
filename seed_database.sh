#!/bin/bash

rm db.sqlite3
rm -rf ./gondorapi/migrations
python manage.py makemigrations gondorapi
python manage.py migrate gondorapi
python manage.py loaddata groups
python manage.py loaddata users
python manage.py loaddata states
python manage.py loaddata address_types
python manage.py loaddata addresses
python manage.py loaddata user_addresses
python manage.py loaddata patient_clinicians

python manage.py seed_appointments
python manage.py seed_patient_data

python manage.py migrate

python manage.py loaddata tokens
python manage.py migrate