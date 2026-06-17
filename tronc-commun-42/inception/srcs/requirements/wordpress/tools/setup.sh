#!/bin/bash
set -e

DB_PASSWORD=$(cat /run/secrets/db_password)
WP_ADMIN_PASSWORD=$(sed -n '1p' /run/secrets/credentials)
WP_USER_PASSWORD=$(sed -n '2p' /run/secrets/credentials)

cd /var/www/html

# Attendre que MariaDB réponde
echo "[wordpress] Attente de MariaDB..."
DB_H="${WORDPRESS_DB_HOST%%:*}"
until mariadb -h"${DB_H}" -u"${MYSQL_USER}" -p"${DB_PASSWORD}" \
        -e "SELECT 1;" "${MYSQL_DATABASE}" >/dev/null 2>&1; do
    sleep 2
done
echo "[wordpress] MariaDB est prête."

if [ ! -f wp-config.php ]; then
    echo "[wordpress] Installation de WordPress..."
    wp core download --allow-root

    wp config create --allow-root \
        --dbname="${MYSQL_DATABASE}" \
        --dbuser="${MYSQL_USER}" \
        --dbpass="${DB_PASSWORD}" \
        --dbhost="${WORDPRESS_DB_HOST}"

    wp core install --allow-root \
        --url="https://${DOMAIN_NAME}" \
        --title="${WP_TITLE}" \
        --admin_user="${WP_ADMIN_USER}" \
        --admin_password="${WP_ADMIN_PASSWORD}" \
        --admin_email="${WP_ADMIN_EMAIL}" \
        --skip-email

    wp user create --allow-root \
        "${WP_USER}" "${WP_USER_EMAIL}" \
        --role=author \
        --user_pass="${WP_USER_PASSWORD}"

    echo "[wordpress] Installation terminée."
fi

chown -R www-data:www-data /var/www/html

# php-fpm en avant-plan, devient PID 1 (pas de hack)
exec /usr/sbin/php-fpm8.2 -F
