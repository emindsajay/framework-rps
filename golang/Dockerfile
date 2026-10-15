FROM golang:1.27.2-bookworm AS build

WORKDIR /src
COPY go.mod main.go ./
RUN go mod tidy \
    && CGO_ENABLED=0 go build -trimpath -ldflags="-s -w" -o /out/server .

FROM debian:bookworm-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=build /out/server /server

EXPOSE 8081

ENTRYPOINT ["/server"]
