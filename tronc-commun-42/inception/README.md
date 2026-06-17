*This project has been created as part of the 42 curriculum by omischle.*

## Description

Inception is a system administration exercise that uses Docker to set up a small infrastructure composed of three services: Nginx (reverse proxy with TLS), WordPress (PHP-FPM), and MariaDB (database). Each service runs in its own dedicated container built from a Debian Bookworm base image.

## Instructions

### Prerequisites

- Docker and Docker Compose v2 installed
- The `secrets/` directory populated with the three secret files (see DEV_DOC.md)
- `/etc/hosts` entry: `127.0.0.1 omischle.42.fr`

### Starting the project

```bash
make
```

### Stopping the project

```bash
make down
```

### Full cleanup (removes volumes and data)

```bash
make fclean
```

## Resources

- [Docker documentation](https://docs.docker.com/)
- [WordPress CLI (wp-cli)](https://wp-cli.org/)
- [MariaDB documentation](https://mariadb.com/kb/en/)
- [Nginx documentation](https://nginx.org/en/docs/)
- [php-fpm documentation](https://www.php.net/manual/en/install.fpm.php)

## Project description

### VM vs Docker

A **Virtual Machine** emulates an entire operating system and hardware stack, providing strong isolation but consuming significant resources (gigabytes of disk, minutes to boot). **Docker containers** share the host OS kernel; they package only the application and its dependencies, start in seconds, and use far fewer resources. Inception uses Docker so each service (nginx, WordPress, MariaDB) runs in an isolated, reproducible, lightweight environment without the overhead of full VMs.

### Secrets vs Environment Variables

**Environment variables** (stored in `srcs/.env`) hold non-sensitive configuration such as domain names, database names, and usernames. They are readable by anyone with file access and are safe to version-control as long as they contain no passwords. **Docker secrets** (stored in `secrets/*.txt` and mounted at `/run/secrets/` inside containers) are the correct mechanism for sensitive data: passwords are never embedded in images, never appear in `docker inspect`, and are only readable by the processes that explicitly need them.

### Docker Network vs Host Network

With **host networking**, containers share the host's network namespace — every port a container listens on is immediately exposed on the host, which breaks isolation. With a **Docker bridge network** (used here as `inception`), containers communicate with each other by service name (e.g., `mariadb`, `wordpress`) on an isolated virtual network. Only the ports explicitly declared in `ports:` (here only 443/tcp) are exposed to the outside world.

### Docker Volumes vs Bind Mounts

**Bind mounts** directly map a host path into a container. They are simple but tightly couple the container to the host filesystem layout and are harder to manage in production. **Named volumes** are managed by Docker and are portable and self-documenting. Inception uses named volumes configured with `driver: local` and `driver_opts` to physically store data in `/home/omischle/data/` while still benefiting from Docker's volume management (listing, inspection, cleanup via `docker volume` commands).
