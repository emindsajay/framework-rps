# Requests per second: Laravel, Spring Boot, Express, Fastify, Bun, FastAPI, and Go

This repository compares how much throughput each stack delivers for the same tiny API, on the same machine, with the same CPU, memory, and database limits.

Each application exposes `GET /api/ping`. Each request runs `SELECT 1` on one PostgreSQL database and returns:

```json
{"status":"ok"}
```

The benchmark runs one application at a time, so the stacks do not compete for CPU. Measured on 15 October 2026 on an Apple M1 Pro (10 CPU cores, 16 GB memory) with Docker 29.2.1. Each application was limited to 2 CPUs and 2 GB. PostgreSQL was limited to 1 CPU and 1 GB.

Use these numbers to compare the stacks on this workload. Re-run the benchmark on the target servers before using them as a capacity plan.

## Result

Go handled the most requests. Express and Spring Boot stayed close behind it. Laravel handled this ping far more slowly, and it started failing once the client count rose.

| Rank | Stack | Highest stable RPS | At | p95 | Compared with Laravel |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | Go 1.27 | 24,690.1 | 200 VUs | 37.7 ms | 29.9× |
| 2 | Express 5.3 on Node.js 24 | 21,603.6 | 25 VUs | 2.1 ms | 26.2× |
| 3 | Spring Boot 3.5 on Java 21 | 21,049.0 | 400 VUs | 50.2 ms | 25.5× |
| 4 | Bun 1.4 | 18,037.5 | 400 VUs | 52.4 ms | 21.8× |
| 5 | Fastify 5.12 on Node.js 24 | 13,632.1 | 100 VUs | 30.2 ms | 16.5× |
| 6 | FastAPI 0.143 on Python 3.14 | 8,820.8 | 25 VUs | 5.0 ms | 10.7× |
| 7 | Laravel 12 on PHP 8.4 | 825.6 | 25 VUs | 88.2 ms | 1.0× |

A level is stable when every repeat has an error rate under 1%, at least 99% of response checks passing, and p95 latency under 500 ms. The rate above is the highest mean of three 30-second repeats among stable levels.

Most stacks were already near their ceiling at 25 virtual users. Adding users raised latency more than throughput. Go still gained throughput through 200 users, and Spring Boot and Bun still gained through 400. FastAPI's best rate was at 25 users.

Laravel stayed near 700–830 RPS at every level. At 200 and 400 virtual users it was unstable: the worst error rates were 1.95% and 4.63%, and p99 latency hit the 10 second client timeout. Extra clients waited or failed. They did not raise throughput.

### Throughput at each concurrency level

Mean of three repeats. Latency is in milliseconds.

| App | VUs | Mean RPS | p50 | p95 | p99 | Error rate | Stable |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Go | 25 | 22,899.5 | 0.6 | 2.2 | 10.8 | 0.00% | yes |
| Go | 50 | 23,836.3 | 1.0 | 3.8 | 34.9 | 0.00% | yes |
| Go | 100 | 23,856.2 | 2.0 | 11.9 | 43.4 | 0.00% | yes |
| Go | 200 | 24,690.1 | 4.0 | 37.7 | 50.5 | 0.00% | yes |
| Go | 400 | 24,050.6 | 8.6 | 52.7 | 80.4 | 0.00% | yes |
| Express | 25 | 21,603.6 | 0.8 | 2.1 | 6.0 | 0.00% | yes |
| Express | 50 | 19,811.3 | 1.7 | 4.6 | 21.1 | 0.00% | yes |
| Express | 100 | 19,349.0 | 3.5 | 13.9 | 32.4 | 0.00% | yes |
| Express | 200 | 18,585.0 | 7.4 | 30.0 | 44.4 | 0.00% | yes |
| Express | 400 | 18,221.6 | 17.0 | 44.5 | 70.4 | 0.00% | yes |
| Spring Boot | 25 | 17,822.4 | 0.7 | 2.1 | 28.9 | 0.00% | yes |
| Spring Boot | 50 | 18,859.9 | 1.2 | 4.5 | 44.3 | 0.00% | yes |
| Spring Boot | 100 | 20,073.4 | 2.1 | 20.7 | 51.4 | 0.00% | yes |
| Spring Boot | 200 | 20,982.6 | 4.0 | 40.9 | 58.4 | 0.00% | yes |
| Spring Boot | 400 | 21,049.0 | 8.5 | 50.2 | 80.3 | 0.00% | yes |
| Bun | 25 | 16,431.6 | 0.8 | 2.6 | 26.9 | 0.00% | yes |
| Bun | 50 | 16,117.6 | 1.4 | 6.1 | 43.0 | 0.00% | yes |
| Bun | 100 | 16,302.8 | 3.0 | 32.1 | 47.7 | 0.00% | yes |
| Bun | 200 | 17,740.8 | 6.3 | 41.3 | 55.5 | 0.00% | yes |
| Bun | 400 | 18,037.5 | 14.4 | 52.4 | 85.7 | 0.00% | yes |
| Fastify | 25 | 12,629.6 | 1.1 | 4.3 | 21.5 | 0.00% | yes |
| Fastify | 50 | 13,239.7 | 2.1 | 8.5 | 37.2 | 0.00% | yes |
| Fastify | 100 | 13,632.1 | 4.3 | 30.2 | 44.2 | 0.00% | yes |
| Fastify | 200 | 12,359.3 | 10.1 | 43.7 | 65.9 | 0.00% | yes |
| Fastify | 400 | 11,073.3 | 27.2 | 73.7 | 133.9 | 0.00% | yes |
| FastAPI | 25 | 8,820.8 | 2.2 | 5.0 | 12.1 | 0.00% | yes |
| FastAPI | 50 | 8,223.0 | 4.6 | 12.2 | 33.7 | 0.00% | yes |
| FastAPI | 100 | 6,673.6 | 10.1 | 35.7 | 93.1 | 0.00% | yes |
| FastAPI | 200 | 8,480.2 | 19.3 | 47.6 | 93.1 | 0.00% | yes |
| FastAPI | 400 | 7,867.7 | 41.5 | 108.6 | 224.4 | 0.00% | yes |
| Laravel | 25 | 825.6 | 8.2 | 88.2 | 99.6 | 0.00% | yes |
| Laravel | 50 | 759.3 | 84.0 | 108.9 | 198.2 | 0.02% | yes |
| Laravel | 100 | 706.0 | 85.0 | 163.6 | 398.1 | 0.64% | yes |
| Laravel | 200 | 716.9 | 84.5 | 186.6 | 10,000.1 | 1.95% | no |
| Laravel | 400 | 730.6 | 86.0 | 269.3 | 10,003.5 | 4.63% | no |

## What this is useful for

This is a ceiling for a trivial, database-backed read:

- The handler does no authentication, validation, serialization of a large body, or business work.
- The SQL is `SELECT 1`. A real query that reads rows will lower every number, and the gap between stacks will usually shrink because more time is spent in PostgreSQL.
- Every stack had the same 2 CPU and 2 GB budget and the same cap of 50 database connections. A service given more CPU, or several replicas, can serve more traffic than the single container measured here.
- Laravel's gap on this test comes from work the framework does on every request: booting the application, setting the PostgreSQL search path, and deallocating prepared statements. The other stacks keep the process warm and send `SELECT 1` once.

Choose a stack with team skill, libraries, and the shape of the real API in mind. Use this benchmark when raw request throughput of a small database-backed endpoint is one of the deciding factors.

## How the comparison was kept fair

- One application runs at a time.
- Each application gets 2 CPUs and 2 GB. PostgreSQL gets 1 CPU, 1 GB, and `max_connections=200`.
- `APP_CONCURRENCY=50` is the shared database-connection cap. Laravel uses 50 PHP-FPM workers with one persistent connection each. Spring Boot uses 50 Tomcat threads and a Hikari pool of 50. Express, Fastify, Bun, and FastAPI each run two processes and give each process 25 connections. Go uses one process with `GOMAXPROCS=2` and a pool of 50.
- PHP-FPM needs the 2 GB limit. Fifty worker processes do not fit comfortably in 1 GB.
- Nginx is pinned to 2 worker processes so it matches the 2 CPU limit. `worker_processes auto` was counting the host's CPUs.
- Production Laravel caches config, routes, views, and events, and OPcache has timestamp checks off.
- Request access logs are off on every stack.
- Laravel session, cache, and queue drivers use local files. The ping does not read them.
- k6 uses a constant number of virtual users and keeps connections open for about 65 seconds, matching each server's keep-alive timeout.
- Each level is warmed for 30 seconds at 50 virtual users, then measured for 30 seconds at 25, 50, 100, 200, and 400 virtual users, three times. The reported RPS is the mean. Stability uses the worst repeat.
- The success body is exactly `{"status":"ok"}`.

## What still differs, because the stacks differ

- Laravel boots the framework on every request. The other stacks keep the application in memory.
- Laravel's default PostgreSQL setup runs `SET search_path TO "public"` and then `SELECT 1` on every request, and deallocates both prepared statements. The search path is applied again even though the connection stays open. The other stacks send `SELECT 1` once.
- Spring Boot uses 50 platform Tomcat threads. Virtual threads are off. Express, Fastify, Bun, and FastAPI each use one event loop per process. Go uses goroutines on 2 OS threads.
- JDBC and Go's `database/sql` may reuse a server-side prepared statement. Laravel uses PDO's default PostgreSQL prepared statements. Express and Fastify use `pg`, which sends a simple query. Bun's SQL client and FastAPI's asyncpg use the PostgreSQL binary protocol.
- FastAPI's generated docs routes are turned off, so the only route is the ping.
- Uvicorn is installed with its standard extras, including uvloop and httptools.

## Versions

| Stack | Runtime and libraries |
| --- | --- |
| Laravel | Skeleton 12.12.2, framework 12.69.3, PHP 8.4, Nginx, PHP-FPM |
| Spring Boot | 3.5.16, Java 21, embedded Tomcat, HikariCP |
| Express | Node.js 24.21.0, Express 5.3.0, `pg` 8.23.1 |
| Fastify | Node.js 24.21.0, Fastify 5.12.7, `pg` 8.23.1 |
| Bun | 1.4.3, `Bun.serve`, built-in `Bun.SQL` |
| FastAPI | Python 3.14.8, FastAPI 0.143.1, Uvicorn 0.54.0, asyncpg 0.32.0 |
| Go | 1.27.2, `net/http`, `database/sql`, pgx 5.11.0 |
| Database | PostgreSQL 17 |
| Load generator | k6 2.3.0 |

## Reproduce the benchmark

Docker is required.

Start the APIs:

```bash
./scripts/up.sh
```

| Stack | On your machine | Inside the benchmark network |
| --- | --- | --- |
| Laravel | http://127.0.0.1:8000/api/ping | http://laravel/api/ping |
| Spring Boot | http://127.0.0.1:8080/api/ping | http://springboot:8080/api/ping |
| Express | http://127.0.0.1:3001/api/ping | http://nodejs:3000/api/ping |
| Fastify | http://127.0.0.1:3002/api/ping | http://fastify:3000/api/ping |
| Bun | http://127.0.0.1:3003/api/ping | http://bun:3000/api/ping |
| FastAPI | http://127.0.0.1:8010/api/ping | http://fastapi:8000/api/ping |
| Go | http://127.0.0.1:8090/api/ping | http://golang:8081/api/ping |

Run every stack. This replaces the result files for every application:

```bash
./scripts/benchmark.sh
```

Measure one stack and keep the other result files:

```bash
APPS=golang ./scripts/benchmark.sh
```

A shorter check:

```bash
LEVELS="25" DURATION=10s WARMUP=10s REPEATS=1 APPS=laravel ./scripts/benchmark.sh
```

`scripts/summarize.py` rewrites `results/summary.md`, `results/summary.csv`, and `results/raw.csv` from every `results/*.json` file. The raw k6 files are local. They are listed in `.gitignore`, so the tables in this README are the copy to share.

Stop everything:

```bash
docker compose down
```

## Layout

| Path | What it contains |
| --- | --- |
| `laravel/` | PHP 8.4, Nginx, and the Laravel 12 ping |
| `springboot/` | Spring Boot 3.5 ping |
| `nodejs/` | Express ping |
| `fastify/` | Fastify ping |
| `bun/` | Bun ping |
| `fastapi/` | FastAPI ping |
| `golang/` | Go ping |
| `k6/ping.js` | Load test |
| `scripts/benchmark.sh` | Build, measure, and summarize |
| `scripts/summarize.py` | Stability rules and the report |
| `docker-compose.yml` | Resource limits and the shared database |
