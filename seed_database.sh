#!/bin/bash

rm db.sqlite3
rm -rf ./gondorapi/migrations
python manage.py makemigrations gondorapi
python manage.py migrate gondorapi
python manage.py loaddata groups
# python manage.py loaddata users
# python manage.py loaddata tokens

python manage.py migrate