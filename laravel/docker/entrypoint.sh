#!/bin/sh
set -eu

concurrency="${APP_CONCURRENCY:-50}"
case "$concurrency" in
    ''|*[!0-9]*)
        echo "APP_CONCURRENCY must be a positive integer" >&2
        exit 1
        ;;
esac

sed "s/__APP_CONCURRENCY__/${concurrency}/g" \
    /usr/local/etc/php-fpm.d/www.conf.template \
    > /usr/local/etc/php-fpm.d/www.conf

sed "s/__APP_CONCURRENCY__/${concurrency}/g" \
    /etc/nginx/nginx.conf.template \
    > /etc/nginx/nginx.conf

cd /var/www/html
php artisan optimize --no-interaction
chown -R www-data:www-data storage bootstrap/cache

exec /usr/bin/supervisord -c /etc/supervisor/supervisord.conf
