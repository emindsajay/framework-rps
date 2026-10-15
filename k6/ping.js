import http from 'k6/http';
import { check } from 'k6';

const vus = Number(__ENV.VUS || 10);
const duration = __ENV.DURATION || '30s';

export const options = {
  scenarios: {
    ping: {
      executor: 'constant-vus',
      vus,
      duration,
      gracefulStop: '2s',
    },
  },
  summaryTrendStats: ['avg', 'min', 'med', 'p(90)', 'p(95)', 'p(99)', 'max'],
};

export default function () {
  const response = http.get(__ENV.TARGET_URL, {
    headers: { Accept: 'application/json' },
    timeout: '10s',
    tags: { name: 'GET /api/ping' },
  });

  check(response, {
    'status is 200': (r) => r.status === 200,
    'body status is ok': (r) => {
      try {
        return r.json('status') === 'ok';
      } catch (_) {
        return false;
      }
    },
  });
}

export function handleSummary(data) {
  if (__ENV.WRITE_SUMMARY !== 'true') {
    return {};
  }

  const latency = data.metrics.http_req_duration.values;

  const summary = {
    app: __ENV.APP_NAME,
    vus: Number(__ENV.VUS),
    repeat: Number(__ENV.REPEAT),
    duration: __ENV.DURATION,
    rps: data.metrics.http_reqs.values.rate,
    requests: data.metrics.http_reqs.values.count,
    failed_rate: data.metrics.http_req_failed.values.rate,
    checks_rate: data.metrics.checks ? data.metrics.checks.values.rate : 0,
    avg_ms: latency.avg,
    p50_ms: latency.med,
    p95_ms: latency['p(95)'],
    p99_ms: latency['p(99)'],
  };

  return {
    [`/results/${__ENV.RESULT_NAME}.json`]: JSON.stringify(summary, null, 2),
  };
}
