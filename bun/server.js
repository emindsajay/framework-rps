const port = Number(process.env.PORT || 3000);
const workers = Number(process.env.WEB_CONCURRENCY || 2);
const poolMax = Number(process.env.APP_CONCURRENCY || 50);

if (!Number.isInteger(workers) || workers < 1) {
  throw new Error("WEB_CONCURRENCY must be a positive integer");
}

if (!Number.isInteger(poolMax) || poolMax < workers) {
  throw new Error("APP_CONCURRENCY must be an integer of at least WEB_CONCURRENCY");
}

if (process.env.BUN_WORKER !== "1") {
  const children = new Set();
  let shuttingDown = false;

  const spawnWorker = () => {
    const child = Bun.spawn({
      cmd: [process.execPath, import.meta.path],
      env: { ...process.env, BUN_WORKER: "1" },
      stdout: "inherit",
      stderr: "inherit",
    });
    children.add(child);
    child.exited.then(() => {
      children.delete(child);
      if (!shuttingDown) {
        spawnWorker();
      }
    });
  };

  for (let i = 0; i < workers; i += 1) {
    spawnWorker();
  }

  process.on("SIGTERM", () => {
    shuttingDown = true;
    for (const child of children) {
      child.kill("SIGTERM");
    }
    process.exit(0);
  });
} else {
  const { SQL } = await import("bun");
  const poolSize = Math.floor(poolMax / workers);
  const sql = new SQL({
    hostname: process.env.DB_HOST || "postgres",
    port: Number(process.env.DB_PORT || 5432),
    database: process.env.DB_DATABASE || "rps",
    username: process.env.DB_USERNAME || "rps",
    password: process.env.DB_PASSWORD || "rps",
    max: poolSize,
    idleTimeout: 0,
    maxLifetime: 0,
    connectionTimeout: 10,
  });

  await Promise.all(Array.from({ length: poolSize }, () => sql`SELECT 1`));

  const server = Bun.serve({
    port,
    hostname: "0.0.0.0",
    reusePort: true,
    idleTimeout: 65,
    async fetch(request) {
      const url = new URL(request.url);
      if (request.method !== "GET" || url.pathname !== "/api/ping") {
        return new Response("Not Found", { status: 404 });
      }

      try {
        await sql`SELECT 1`;
        return new Response('{"status":"ok"}', {
          headers: { "content-type": "application/json" },
        });
      } catch {
        return new Response('{"message":"Server Error"}', {
          status: 500,
          headers: { "content-type": "application/json" },
        });
      }
    },
  });

  process.on("SIGTERM", async () => {
    await server.stop(true);
    await sql.close();
    process.exit(0);
  });
}
