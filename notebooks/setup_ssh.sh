# #!/bin/bash

# # Switch to root
# sudo su - <<EOF
# apt update && apt install -y openssh-server

# mkdir -p /var/run/sshd

# echo 'root:password' | chpasswd

# sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config

# /usr/sbin/sshd

# echo "SSH server setup complete. You can connect using:"


#!/bin/bash

# Become root
sudo su - <<'EOF'

# Update and install ssh server
apt update && apt install -y openssh-server sudo

# Make sure sshd can run
mkdir -p /var/run/sshd

# Set root password (change 'password' to secure one)
echo 'root:password' | chpasswd

# Allow root login with password via SSH
sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config

# Allow password authentication (for both root and docker)
sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config

# Grant docker user passwordless sudo (full root privilege)
echo "docker ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/docker
chmod 440 /etc/sudoers.d/docker

# Set docker user password (change 'password' accordingly)
echo 'docker:password' | chpasswd

# Start ssh service
/usr/sbin/sshd

echo "✅ SSH server started, root and docker users can login with password."



echo "RUNNING FASTAPI SERVER"
chmod -R 777 /home/docker/notebooks/
pip install -r /home/docker/notebooks/requirements.txt || { echo "Failed to install requirements"; exit 1; }

cd /home/docker/notebooks/fastapi/ || { echo "Directory not found"; exit 1; }

python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

echo "FastAPI server is running at http://localhost:8000"


EOF