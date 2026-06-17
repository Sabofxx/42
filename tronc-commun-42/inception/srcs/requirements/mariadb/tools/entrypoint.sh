#!/bin/bash
set -e

DB_ROOT_PASSWORD=$(cat /run/secrets/db_root_password)
DB_PASSWORD=$(cat /run/secrets/db_password)

mkdir -p /run/mysqld
chown mysql:mysql /run/mysqld

if [ ! -f "/var/lib/mysql/.initialized" ]; then
    echo "[mariadb] First start: setting up database and user..."

    mysqld --user=mysql --skip-networking --socket=/run/mysqld/mysqld.sock &
    MYSQLD_PID=$!

    until mysqladmin --socket=/run/mysqld/mysqld.sock ping --silent 2>/dev/null; do
        sleep 1
    done

    mysql --socket=/run/mysqld/mysqld.sock -uroot -e "
        FLUSH PRIVILEGES;
        ALTER USER 'root'@'localhost' IDENTIFIED BY '${DB_ROOT_PASSWORD}';
        CREATE DATABASE IF NOT EXISTS \`${MYSQL_DATABASE}\`;
        CREATE USER IF NOT EXISTS '${MYSQL_USER}'@'%' IDENTIFIED BY '${DB_PASSWORD}';
        GRANT ALL PRIVILEGES ON \`${MYSQL_DATABASE}\`.* TO '${MYSQL_USER}'@'%';
        FLUSH PRIVILEGES;
    "

    touch /var/lib/mysql/.initialized
    echo "[mariadb] Setup complete."

    kill "${MYSQLD_PID}"
    wait "${MYSQLD_PID}" 2>/dev/null || true
fi

exec mysqld --user=mysql
