FROM composer:2 AS source

WORKDIR /app

RUN composer create-project laravel/laravel:12.12.2 . \
        --no-dev \
        --no-interaction \
        --prefer-dist \
        --no-scripts \
        --no-install

COPY overlay/bootstrap/app.php bootstrap/app.php
COPY overlay/routes/api.php routes/api.php
COPY overlay/app/Providers/AppServiceProvider.php app/Providers/AppServiceProvider.php
COPY overlay/app/Http/Controllers/PingController.php app/Http/Controllers/PingController.php
COPY overlay/.env .env

RUN composer require laravel/framework:12.69.3 \
        --no-interaction \
        --no-scripts \
        --prefer-dist \
        --update-no-dev \
        --update-with-dependencies \
        --optimize-autoloader \
        --classmap-authoritative

FROM php:8.4-fpm-bookworm

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        nginx \
        supervisor \
        curl \
        ca-certificates \
        libpq-dev \
    && docker-php-ext-install -j"$(nproc)" pdo_pgsql \
    && docker-php-ext-enable opcache \
    && apt-get purge -y --auto-remove libpq-dev \
    && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && rm -f /usr/local/etc/php-fpm.d/*

COPY --from=source /app /var/www/html
COPY docker/nginx.conf.template /etc/nginx/nginx.conf.template
COPY docker/www.conf.template /usr/local/etc/php-fpm.d/www.conf.template
COPY docker/opcache.ini /usr/local/etc/php/conf.d/opcache.ini
COPY docker/php.ini /usr/local/etc/php/conf.d/zz-bench.ini
COPY docker/supervisord.conf /etc/supervisor/supervisord.conf
COPY docker/entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh \
    && mkdir -p \
        /var/www/html/storage/framework/cache/data \
        /var/www/html/storage/framework/sessions \
        /var/www/html/storage/framework/views \
        /var/www/html/storage/logs \
        /var/www/html/bootstrap/cache \
        /var/log/nginx \
        /tmp/nginx \
    && chown -R www-data:www-data /var/www/html/storage /var/www/html/bootstrap/cache \
    && rm -f /etc/nginx/sites-enabled/default

EXPOSE 80

ENTRYPOINT ["/entrypoint.sh"]
