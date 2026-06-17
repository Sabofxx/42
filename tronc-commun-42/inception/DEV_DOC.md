# Developer Documentation — Inception

## Setup from scratch

### 1. Prerequisites

- Debian-based VM with Docker Engine and Docker Compose v2 installed
- User added to the `docker` group (or use `sudo`)
- Port 443 not in use by the host

### 2. Clone / obtain the project

Place the project root at any path, for example `/home/omischle/Desktop/`.

### 3. Create secrets

Create the `secrets/` directory at the project root and add three files:

```bash
mkdir -p secrets
echo "YourRootPassword"  > secrets/db_root_password.txt
echo "YourDbPassword"    > secrets/db_password.txt
# Line 1 = WP admin password, Line 2 = WP author password
printf "WpAdminPassword\nWpAuthorPassword\n" > secrets/credentials.txt
```

> `secrets/` is in `.gitignore` — never commit it.

### 4. Configure `/etc/hosts`

```bash
echo "127.0.0.1  omischle.42.fr" | sudo tee -a /etc/hosts
```

### 5. Build and launch

```bash
cd /home/omischle/Desktop
make
```

`make` (alias for `make up`) will:
1. Create `/home/omischle/data/db` and `/home/omischle/data/wp` on the host.
2. Build all three images from their Dockerfiles.
3. Start the containers in detached mode.

## Project structure

```
.
├── Makefile
├── .gitignore
├── secrets/          ← NOT committed (passwords)
├── srcs/
│   ├── .env          ← Non-sensitive variables
│   ├── docker-compose.yml
│   └── requirements/
│       ├── mariadb/
│       │   ├── Dockerfile
│       │   ├── conf/my.cnf
│       │   └── tools/entrypoint.sh
│       ├── nginx/
│       │   ├── Dockerfile
│       │   └── conf/nginx.conf
│       └── wordpress/
│           ├── Dockerfile
│           ├── conf/www.conf
│           └── tools/entrypoint.sh
```

## Makefile targets

| Target | Action |
|--------|--------|
| `all` / `up` | Create data dirs, build images, start containers |
| `build` | Build images only |
| `down` | Stop and remove containers |
| `stop` | Stop containers (preserve state) |
| `start` | Start stopped containers |
| `re` | `clean` then `up` |
| `clean` | `down` + remove named volumes |
| `fclean` | `clean` + `docker system prune` + `rm -rf /home/omischle/data` |
| `logs` | Follow all container logs |
| `ps` | Show container status |

## Container and volume commands

```bash
# Enter a running container
docker exec -it mariadb bash
docker exec -it wordpress bash
docker exec -it nginx bash

# Check MariaDB from inside its container
docker exec mariadb mysql -uroot -p"$(cat secrets/db_root_password.txt)" -e "SHOW DATABASES;"

# List WordPress users
docker exec wordpress wp user list --allow-root --path=/var/www/html

# Inspect named volumes
docker volume ls
docker volume inspect srcs_mariadb
docker volume inspect srcs_wordpress
```

## Where data is stored and how it persists

Both named volumes use `driver: local` with `driver_opts` to bind-mount host directories:

| Volume | Host path | Container path |
|--------|-----------|----------------|
| `mariadb` | `/home/omischle/data/db` | `/var/lib/mysql` |
| `wordpress` | `/home/omischle/data/wp` | `/var/www/html` |

Data survives `make down` and `make stop`. Only `make fclean` removes it.

## TLS configuration

The Nginx container generates a self-signed RSA-2048 certificate at build time using OpenSSL. The certificate covers `omischle.42.fr` and is valid for 365 days. Only `TLSv1.2` and `TLSv1.3` are enabled; older protocols (TLSv1.0, TLSv1.1) and weak ciphers are explicitly excluded.

Verify with:
```bash
openssl s_client -connect omischle.42.fr:443 -tls1_2
openssl s_client -connect omischle.42.fr:443 -tls1_3
# The following should FAIL:
openssl s_client -connect omischle.42.fr:443 -tls1_1
```
