# Install Stackdriver logging agent
curl -sSO https:/dl.google.com/cloudagents/install-logging-agent.sh
sudo bash install-logging-agent.sh

# Install or update needed software
apt-get update
apt install software-properties-common
add-apt-repository ppa:deadsnakes/ppa -y
apt-get install -yq git supervisor python python-pip python3-dev python3.7
pip install --upgrade pip virtualenv

# Account to own server process
useradd -m -d /home/pythonapp pythonapp

# Fetch source code
export HOME=/root
git clone https://github.com/marvel-dic/vocabulizer.git /opt/app -b minimal_gcp_app
cd /opt/app
git pull
git checkout

# Database setup
apt-get install postgresql postgresql-contrib


# Python environment setup
virtualenv -p python3.7 /opt/app/env
source /opt/app/env/bin/activate
/opt/app/env/bin/pip install -r /opt/app/requirements.txt
/opt/app/env/bin/python download en_core_web_sm
# /opt/app/env/bin/python download en_core_web_lg

# Set ownership to newly created account
chown -R pythonapp:pythonapp /opt/app

# Put supervisor configuration in proper place
cp /opt/app/python-app.conf /etc/supervisor/conf.d/python-app.conf

# Start service via supervisorctl
supervisorctl reread
supervisorctl update