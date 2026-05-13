# PIA LARA

## Creating the AWS instance
- Key LARA.pem
- Instance type t3.small
- Name ProyectoLARA
- Fixed IP https://18.214.200.16/

## Adding the keys to AWS Secrets Manager
We have the keys locally, they are as follows:

- SECRET_KEY = eac5e91171438960ddec0c9c469a4c3dd42e96aea462afc5ab830f78527ad80e
- PIALARA_DB_URI = mongo
- PIALARA_DB_NAME = prelara
- BUCKET_NAME = pialara
- GRADIO_URL = http://localhost:8080/gradio

We search for the Secrets Manager service and store a new secret.

Other type of secret --> Plain text (in JSON format)

We insert the following:
``` 
{
"SECRET_KEY":"eac5e91171438960ddec0c9c469a4c3dd42e96aea462afc5ab830f78527ad80e",
PIALARA_DB_URI":"mongo",
PIALARA_DB_NAME":"prelara",
BUCKET_NAME":"pialara",
GRADIO_URL":"http://localhost:8080/gradio"
}
```
Name PIALARA
- We store the secret

## Installing Docker on the AWS instance
Copy and paste

``` 
# Add Docker's official GPG key:
sudo apt update
sudo apt install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
sudo tee /etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
EOF

sudo apt update
``` 

``` 
sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

```
sudo usermod -aG docker ubuntu
``` 

``` 
sudo usermod -aG $USER
``` 

``` 
newgrp
``` 

``` 
newgrp docker
``` 

## Downloading the project via HTTPS (without key)
- git clone https://github.com/MarcosGarciaR/pia-lara.git 
- cd pia-lara/
- git checkout feature-sevilla-despliegueawssecrets 

This way we would not have keys in the GitHub repository either.

## Assigning the role to the instance to access AWS keys
In the instance console on AWS
- Actions → Security → Modify IAM role
- Select LabInstanceProfile, this role has the necessary permissions for the lab (it can access Secrets Manager)
- Update role

Verify key access on the instance
``` 
sudo apt install -y awscli
aws secretsmanager get-secret-value --secret-id PIALARA --region us-east-1
```

## Starting the database container
- scp -i LARA.pem dump-prelara-260924 ubuntu@18.214.200.16:~/
- docker compose up -d mongo 
- docker cp ~/dump-prelara-260924 mongo-prod:/data/import 
- docker exec -it mongo-prod mongorestore --db prelara /data/import/prelara --drop

- docker compose up -d --build
- docker exec -it flask-prod python3 migrations/sylabus_migration.py

## Configuring NGINX

- sudo apt install -y nginx git curl build-essential

### Creating certificates etc. (so that the microphone works)
- sudo mkdir -p /etc/nginx/ssl 

- sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/nginx/ssl/pialara.key \
  -out /etc/nginx/ssl/pialara.crt

``` 
- Country Name: ES
- State: Sevilla
- Locality: Carmona
- Organization Name: PiaLara
- Common Name: 18.214.200.16
- Email: marcos.garcia.rodriguez.al@iespoligonosur.org
``` 

## Redirects all HTTP to HTTPS
- sudo nano /etc/nginx/sites-available/pialara
```
server {
    listen 80;
    server_name 18.214.200.16;
    return 301 https://$host$request_uri;
}
``` 

### HTTPS with self-signed certificate
``` 
server {
    listen 443 ssl;
    server_name 18.214.200.16;

    ssl_certificate     /etc/nginx/ssl/pialara.crt;
    ssl_certificate_key /etc/nginx/ssl/pialara.key;

    ssl_protocols       TLSv1.2 TLSv1.3;
    ssl_ciphers         HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

- sudo ln -s /etc/nginx/sites-available/pialara /etc/nginx/sites-enabled/
- sudo nginx -t

- sudo systemctl reload nginx 

## Accessing the web
18.214.200.16