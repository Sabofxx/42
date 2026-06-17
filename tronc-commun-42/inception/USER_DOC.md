# User Documentation — Inception

## Services provided

| Service | Description | Access |
|---------|-------------|--------|
| **Nginx** | HTTPS reverse proxy (TLSv1.2/1.3 only) | https://omischle.42.fr |
| **WordPress** | CMS served via PHP-FPM | https://omischle.42.fr |
| **MariaDB** | Database backend (internal only) | Not accessible from outside |

## Starting and stopping

```bash
# Start all services (builds images if needed, creates data directories)
make

# Stop containers without removing them
make stop

# Restart stopped containers
make start

# Stop and remove containers (data is preserved)
make down

# Full cleanup: stop, remove containers, volumes, and all data on disk
make fclean
```

## Accessing the WordPress site

1. Add the following line to `/etc/hosts` on your machine:
   ```
   127.0.0.1  omischle.42.fr
   ```
2. Open your browser and navigate to `https://omischle.42.fr`
3. Accept the self-signed certificate warning.

## Accessing the WordPress admin panel

- URL: `https://omischle.42.fr/wp-admin`
- Admin username: `supervisor` (see `secrets/credentials.txt` line 1 for password)
- Second user: `author42` with role **author** (see `secrets/credentials.txt` line 2 for password)

## Where are the credentials?

| Secret | File | Content |
|--------|------|---------|
| MariaDB root password | `secrets/db_root_password.txt` | Single line |
| MariaDB WordPress user password | `secrets/db_password.txt` | Single line |
| WordPress admin password | `secrets/credentials.txt` | Line 1 |
| WordPress author password | `secrets/credentials.txt` | Line 2 |

> **Note:** The `secrets/` directory is listed in `.gitignore` and must never be committed to version control.

## Verifying that everything is running

```bash
# Check container status
make ps

# Follow logs in real time
make logs

# Test HTTPS response
curl -kI https://omischle.42.fr

# Check WordPress users (run inside the wordpress container)
docker exec wordpress wp user list --allow-root --path=/var/www/html
```

Expected `make ps` output: three containers (`nginx`, `wordpress`, `mariadb`) all with status **Up**.
