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

# Move supervisord.conf to /etc/supervisor/supervisord.conf if missing
sudo mv supervisord.conf /etc/supervisor

# Move celery worker / celery beat configs to /etc/supervisor/conf.d
sudo cp daemonconfs/* /etc/supervisor/conf.d

# Loading environment data
export EB_APP_USER=$(sudo /opt/elasticbeanstalk/bin/get-config platformconfig -k AppUser)
export EB_APP_CURRENT_DIR=$(sudo /opt/elasticbeanstalk/bin/get-config platformconfig -k AppDeployDir)
export PY=$PYTHONPATH
/var/app/venv/*/bin/python3 /var/app/venv/*/bin/supervisord