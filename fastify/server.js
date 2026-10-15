import cluster from 'node:cluster';
import Fastify from 'fastify';
import pg from 'pg';

const port = Number(process.env.PORT || 3000);
const workers = Number(process.env.WEB_CONCURRENCY || 2);
const poolMax = Number(process.env.APP_CONCURRENCY || 50);

if (!Number.isInteger(workers) || workers < 1) {
  throw new Error('WEB_CONCURRENCY must be a positive integer');
}

if (!Number.isInteger(poolMax) || poolMax < workers) {
  throw new Error('APP_CONCURRENCY must be an integer of at least WEB_CONCURRENCY');
}

if (cluster.isPrimary) {
  let shuttingDown = false;

  for (let i = 0; i < workers; i += 1) {
    cluster.fork();
  }

  process.on('SIGTERM', () => {
    shuttingDown = true;
    for (const worker of Object.values(cluster.workers ?? {})) {
      worker.process.kill('SIGTERM');
    }
    process.exit(0);
  });

  cluster.on('exit', () => {
    if (!shuttingDown) {
      cluster.fork();
    }
  });
} else {
  const poolSize = Math.floor(poolMax / workers);
  const pool = new pg.Pool({
    host: process.env.DB_HOST || 'postgres',
    port: Number(process.env.DB_PORT || 5432),
    database: process.env.DB_DATABASE || 'rps',
    user: process.env.DB_USERNAME || 'rps',
    password: process.env.DB_PASSWORD || 'rps',
    max: poolSize,
    idleTimeoutMillis: 0,
    connectionTimeoutMillis: 10000,
  });

  await Promise.all(Array.from({ length: poolSize }, () => pool.query('SELECT 1')));

  const app = Fastify({ logger: false });

  app.get('/api/ping', async () => {
    await pool.query('SELECT 1');
    return { status: 'ok' };
  });

  app.setErrorHandler((_error, _request, reply) => {
    reply.code(500).send({ message: 'Server Error' });
  });

  await app.listen({ port, host: '0.0.0.0' });
  app.server.keepAliveTimeout = 65000;
  app.server.headersTimeout = 66000;

  process.on('SIGTERM', () => {
    app.close().finally(() => {
      pool.end().finally(() => process.exit(0));
    });
  });
}
