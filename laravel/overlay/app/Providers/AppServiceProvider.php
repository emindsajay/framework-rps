<?php

namespace App\Providers;

use Illuminate\Support\ServiceProvider;
use PDO;

class AppServiceProvider extends ServiceProvider
{
    /**
     * Register any application services.
     */
    public function register(): void
    {
        //
    }

    /**
     * Reuse one PostgreSQL connection per PHP-FPM worker.
     *
     * Worker count comes from APP_CONCURRENCY and matches Spring Boot's
     * Hikari pool size. Laravel still applies its default search_path
     * setting on every request.
     */
    public function boot(): void
    {
        config([
            'database.connections.pgsql.options' => [
                PDO::ATTR_PERSISTENT => true,
            ],
        ]);
    }
}
