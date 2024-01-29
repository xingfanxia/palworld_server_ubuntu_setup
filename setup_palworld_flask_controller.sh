#!/bin/bash

# Set these variables
APP_DIR="/home/root/palworld_controller"
APP_USER="root"
APP_GROUP="pal-control"

# Ensure the script is run as root
if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root."
   exit 1
fi

# Update the system
apt update && apt upgrade -y

# Install required packages
apt install -y python3 python3-pip python3-venv nginx

# Create the application directory if it doesn't exist
mkdir -p "$APP_DIR"

# Navigate to application directory
cd "$APP_DIR"

# Set up a Python virtual environment and activate it
python3 -m venv venv
source venv/bin/activate

# Install Flask, Gunicorn, psutil, Flask-HTTPAuth in the virtual environment
pip install Flask gunicorn psutil Flask-HTTPAuth

# Create the Flask application script
cp app.py "$APP_DIR/app.py"

# Create the Gunicorn systemd service file
cat > /etc/systemd/system/palworld_controller.service << EOF
[Unit]
Description=Gunicorn instance to serve palworld_controller
After=network.target

[Service]
User=$APP_USER
Group=$APP_GROUP
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/gunicorn --workers 3 --bind unix:$APP_DIR/palworld_controller.sock -m 007 app:app

[Install]
WantedBy=multi-user.target
EOF

# Start and enable the new service
systemctl start palworld_controller.service
systemctl enable palworld_controller.service

# Create Nginx configuration for the application
cat > /etc/nginx/sites-available/palworld_controller << EOF
server {
    listen 80;
    server_name server_domain_or_IP;

    location / {
        include proxy_params;
        proxy_pass http://unix:$APP_DIR/palworld_controller.sock;
    }
}
EOF

# Link Nginx configuration and restart Nginx
ln -s /etc/nginx/sites-available/palworld_controller /etc/nginx/sites-enabled
systemctl restart nginx

# Print success message
echo "Flask app deployment completed successfully!"