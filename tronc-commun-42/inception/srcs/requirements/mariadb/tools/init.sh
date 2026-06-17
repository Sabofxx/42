#!/bin/bash
set -e

DB_ROOT_PASSWORD=$(cat /run/secrets/db_root_password)
DB_PASSWORD=$(cat /run/secrets/db_password)

# Première initialisation seulement (volume vide)
if [ ! -d "/var/lib/mysql/mysql" ]; then
    echo "[mariadb] Initialisation du répertoire de données..."
    mariadb-install-db --user=mysql --datadir=/var/lib/mysql --skip-test-db >/dev/null

    echo "[mariadb] Création de la base et des utilisateurs..."
    cat > /tmp/init.sql <<EOF
USE mysql;
FLUSH PRIVILEGES;
ALTER USER 'root'@'localhost' IDENTIFIED BY '${DB_ROOT_PASSWORD}';
CREATE DATABASE IF NOT EXISTS \`${MYSQL_DATABASE}\`;
CREATE USER IF NOT EXISTS '${MYSQL_USER}'@'%' IDENTIFIED BY '${DB_PASSWORD}';
GRANT ALL PRIVILEGES ON \`${MYSQL_DATABASE}\`.* TO '${MYSQL_USER}'@'%';
FLUSH PRIVILEGES;
EOF

    mysqld --user=mysql --bootstrap < /tmp/init.sql
    rm -f /tmp/init.sql
    echo "[mariadb] Initialisation terminée."
fi

# mysqld devient PID 1 (pas de hack tail -f / sleep infinity)
exec mysqld --user=mysql
