#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status.
#dropdb helios
#createdb helios
python manage.py makemigrations
python manage.py migrate
echo "from helios_auth.models import User; User.objects.create(user_type='github',user_id='wanghao75', info={'name':'Hao Wang'})" | python manage.py shell
