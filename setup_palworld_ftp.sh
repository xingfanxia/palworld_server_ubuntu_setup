#!/bin/bash

# sudu required

FTP_USER="ftpuser"
FTP_DIR="/home/$FTP_USER/palworld"
FTP_PASS="ChangeMe"  # Change this password!

# Install vsftpd
apt-get update
apt-get install -y vsftpd

# Configure vsftpd
cat << EOF > /etc/vsftpd.conf
listen=NO
listen_ipv6=YES
anonymous_enable=NO
local_enable=YES
write_enable=YES
local_umask=022
dirmessage_enable=YES
use_localtime=YES
xferlog_enable=YES
connect_from_port_20=YES
chroot_local_user=YES
secure_chroot_dir=/var/run/vsftpd/empty
pam_service_name=vsftpd
pasv_enable=YES
pasv_min_port=10000
pasv_max_port=10100
user_sub_token=\$USER
local_root=/home/\$USER/ftp
EOF

# Restart vsftpd service
systemctl restart vsftpd

# Adding new FTP user
adduser --disabled-password --gecos "" $FTP_USER

# Create FTP directory and set permissions
mkdir -p $FTP_DIR
chown nobody:nogroup /home/$FTP_USER
chmod a-w /home/$FTP_USER
chown -R $FTP_USER:$FTP_USER $FTP_DIR
echo $FTP_USER:$FTP_PASS | chpasswd

# Setting up firewall using UFW
ufw allow 20/tcp
ufw allow 21/tcp
ufw allow 10000:10100/tcp
ufw enable
ufw status

echo "FTP server setup complete."