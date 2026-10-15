FROM node:24.21.0-bookworm-slim

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci --omit=dev

COPY server.js .

ENV NODE_ENV=production

EXPOSE 3000

CMD ["node", "server.js"]
