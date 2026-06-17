#!/bin/bash
set -e

DB_PASSWORD=$(cat /run/secrets/db_password)
WP_ADMIN_PASSWORD=$(sed -n '1p' /run/secrets/credentials)
WP_USER_PASSWORD=$(sed -n '2p' /run/secrets/credentials)

WP_PATH=/var/www/html
DB_HOST=$(echo "${WORDPRESS_DB_HOST}" | cut -d: -f1)
DB_PORT=$(echo "${WORDPRESS_DB_HOST}" | cut -d: -f2)

until bash -c ">/dev/tcp/${DB_HOST}/${DB_PORT}" 2>/dev/null; do
    echo "Waiting for MariaDB on ${DB_HOST}:${DB_PORT}..."
    sleep 2
done
sleep 1

if [ ! -f "${WP_PATH}/wp-config.php" ]; then
    wp core download --path="${WP_PATH}" --allow-root

    wp config create \
        --path="${WP_PATH}" \
        --dbname="${MYSQL_DATABASE}" \
        --dbuser="${MYSQL_USER}" \
        --dbpass="${DB_PASSWORD}" \
        --dbhost="${WORDPRESS_DB_HOST}" \
        --allow-root
fi

if ! wp core is-installed --path="${WP_PATH}" --allow-root 2>/dev/null; then
    wp core install \
        --path="${WP_PATH}" \
        --url="https://${DOMAIN_NAME}" \
        --title="${WP_TITLE}" \
        --admin_user="${WP_ADMIN_USER}" \
        --admin_password="${WP_ADMIN_PASSWORD}" \
        --admin_email="${WP_ADMIN_EMAIL}" \
        --allow-root

    wp user create "${WP_USER}" "${WP_USER_EMAIL}" \
        --path="${WP_PATH}" \
        --role=author \
        --user_pass="${WP_USER_PASSWORD}" \
        --allow-root

    chown -R www-data:www-data "${WP_PATH}"
fi

exec php-fpm8.2 -F
