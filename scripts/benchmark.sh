#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"

duration="${DURATION:-30s}"
warmup="${WARMUP:-30s}"
warmup_vus="${WARMUP_VUS:-50}"
repeats="${REPEATS:-3}"
read -r -a levels <<< "${LEVELS:-25 50 100 200 400}"
read -r -a apps <<< "${APPS:-laravel springboot nodejs fastify bun fastapi golang}"

mkdir -p results
chmod 777 results
for app in "${apps[@]}"; do
  find results -type f -name "${app}-vu*.json" -delete
done

echo "==> Building ${apps[*]}"
docker compose build "${apps[@]}"

echo "==> Starting PostgreSQL"
docker compose up -d --wait postgres
docker compose stop laravel springboot nodejs fastify bun fastapi golang >/dev/null 2>&1 || true

run_k6() {
  local app="$1"
  local url="$2"
  local vus="$3"
  local run_duration="$4"
  local repeat="$5"
  local write_summary="$6"
  local result_name="$7"

  docker compose --profile benchmark run --rm --no-deps -T \
    -e APP_NAME="$app" \
    -e TARGET_URL="$url" \
    -e VUS="$vus" \
    -e DURATION="$run_duration" \
    -e REPEAT="$repeat" \
    -e WRITE_SUMMARY="$write_summary" \
    -e RESULT_NAME="$result_name" \
    k6 run --quiet --log-output=none /scripts/ping.js
}

for app in "${apps[@]}"; do
  case "$app" in
    laravel) url="http://laravel/api/ping" ;;
    springboot) url="http://springboot:8080/api/ping" ;;
    nodejs) url="http://nodejs:3000/api/ping" ;;
    fastify) url="http://fastify:3000/api/ping" ;;
    bun) url="http://bun:3000/api/ping" ;;
    fastapi) url="http://fastapi:8000/api/ping" ;;
    golang) url="http://golang:8081/api/ping" ;;
    *)
      echo "Unknown app: ${app}" >&2
      exit 1
      ;;
  esac

  echo "==> Starting ${app}"
  docker compose up -d --wait "$app"

  echo "==> Warming ${app} with ${warmup_vus} virtual users for ${warmup}"
  run_k6 "$app" "$url" "$warmup_vus" "$warmup" 0 false warmup || true

  for vus in "${levels[@]}"; do
    for ((repeat = 1; repeat <= repeats; repeat++)); do
      echo "==> Measuring ${app}: ${vus} virtual users, repeat ${repeat}/${repeats}, ${duration}"
      run_k6 "$app" "$url" "$vus" "$duration" "$repeat" true "${app}-vu${vus}-run${repeat}" || true
    done
  done

  echo "==> Stopping ${app}"
  docker compose stop "$app"
done

python3 scripts/summarize.py
