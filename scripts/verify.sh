#!/usr/bin/env bash
set -euo pipefail

expected='{"status":"ok"}'
laravel="$(curl -fsS -H 'Accept: application/json' http://127.0.0.1:8000/api/ping)"
spring="$(curl -fsS -H 'Accept: application/json' http://127.0.0.1:8080/api/ping)"
nodejs="$(curl -fsS -H 'Accept: application/json' http://127.0.0.1:3001/api/ping)"
fastify="$(curl -fsS -H 'Accept: application/json' http://127.0.0.1:3002/api/ping)"
bun="$(curl -fsS -H 'Accept: application/json' http://127.0.0.1:3003/api/ping)"
fastapi="$(curl -fsS -H 'Accept: application/json' http://127.0.0.1:8010/api/ping)"
golang="$(curl -fsS -H 'Accept: application/json' http://127.0.0.1:8090/api/ping)"

printf 'Laravel:     %s\n' "$laravel"
printf 'Spring Boot: %s\n' "$spring"
printf 'Node.js:     %s\n' "$nodejs"
printf 'Fastify:     %s\n' "$fastify"
printf 'Bun:         %s\n' "$bun"
printf 'FastAPI:     %s\n' "$fastapi"
printf 'Go:          %s\n' "$golang"

if [[ "$laravel" != "$expected" || "$spring" != "$expected" || "$nodejs" != "$expected" || "$fastify" != "$expected" || "$bun" != "$expected" || "$fastapi" != "$expected" || "$golang" != "$expected" ]]; then
  echo "All APIs must return ${expected}" >&2
  exit 1
fi

echo "All APIs returned the same body."
