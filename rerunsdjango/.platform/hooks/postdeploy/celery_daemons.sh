#!/usr/bin/env bash

# Loading environment data
export EB_APP_USER=$(sudo /opt/elasticbeanstalk/bin/get-config platformconfig -k AppUser)
export EB_APP_CURRENT_DIR=$(sudo /opt/elasticbeanstalk/bin/get-config platformconfig -k AppDeployDir)

# Create /etc/supervisor/conf.d directories if missing
cd /etc/
sudo mkdir -p supervisor
cd /etc/supervisor
sudo mkdir -p conf.d

# Create supervisord.conf
cd $EB_APP_CURRENT_DIR
sudo /var/app/venv/*/bin/python3 /var/app/venv/*/bin/echo_supervisord_conf > supervisord.conf

# In supervisord.conf, replace
#  ;[include]
#  ;files = relative/directory/*.ini
# with
#  [include]
#  files = /etc/supervisor/conf.d/*.conf
sudo sed -i 's/;\[include/\[include/' supervisord.conf
sudo sed -i 's/;files = relative\/directory\/\*\.ini/files = \/etc\/supervisor\/conf\.d\/\*\.conf/' supervisord.conf

# replace
#  [unix_http_server]
#  file=/tmp/supervisor.sock   ; the path to the socket file
# with
#  [unix_http_server]
#  file=/var/run/supervisor.sock   ; the path to the socket file
sudo touch /var/run/supervisor.sock
sudo sed -i 's/tmp\/supervisor\.sock/var\/run\/supervisor\.sock/' supervisord.conf

# Move supervisord.conf to /etc/supervisor/supervisord.conf if missing
sudo mv supervisord.conf /etc/supervisor

# Move celery worker / celery beat configs to /etc/supervisor/conf.d
sudo cp daemonconfs/* /etc/supervisor/conf.d

# Loading environment data
export EB_APP_USER=$(sudo /opt/elasticbeanstalk/bin/get-config platformconfig -k AppUser)
export EB_APP_CURRENT_DIR=$(sudo /opt/elasticbeanstalk/bin/get-config platformconfig -k AppDeployDir)
export PY=$PYTHONPATH

## Function to check if a process is alive and running:
## (courtesy of https://askubuntu.com/a/988986)
_isRunning() {
    ps -o comm= -C "$1" 2>/dev/null | grep -x "$1" >/dev/null 2>&1
}

## Start or restart supervisord
if _isRunning supervisord; then
    sudo /var/app/venv/*/bin/python3 /var/app/venv/*/bin/supervisorctl restart
else
    /var/app/venv/*/bin/python3 /var/app/venv/*/bin/supervisord
fi
