#!/bin/bash
pwd
/etc/init.d/postgresql start
/etc/init.d/rabbitmq-server start
cd /app/helios-server
python3.6 -m venv venv 
source /app/helios-server/venv/bin/activate
python3.6 -m pip install -r requirements.txt --quiet
python3.6 -m pip install uwsgi --quiet

/usr/bin/expect<<EOF
spawn sh -c "sudo -u postgres psql"
expect "postgres#="
send "CREATE ROLE root superuser login;\r"
expect "postgres#="
send "exit;\r"
expect eof
EOF

chmod 755 reset.sh
sh /app/helios-server/reset.sh
nohup celery -A helios worker -l INFO>celery.log &
uwsgi --ini uwsgi.ini
