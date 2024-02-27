FROM golang:1.20-alpine AS builder

RUN addgroup -g 50000 -S data \
  && adduser -u 50000 -S data -G data

RUN apk update && apk add --no-cache ca-certificates

# Copy In Source Code
WORKDIR /go/src/app
COPY . .

# Copy In entrypoint.sh
# COPY entrypoint.sh /entrypoint.sh
# RUN chmod 700 /entrypoint.sh \
#   && chown data:data /entrypoint.sh

# Install Dependencies
RUN go mod download && \
    go mod verify
# Build
RUN GOOS=linux GOARCH=amd64 CGO_ENABLED=0 \
    go build -ldflags="-w -s" -o /go/bin/server

RUN mkdir /data && chown data:data /data && chmod 755 /data

# SCRATCH IMAGE
FROM scratch
COPY --from=builder /go/bin/server /go/bin/server
COPY --from=builder /etc/ssl/certs/ca-certificates.crt \
                    /etc/ssl/certs/ca-certificates.crt
COPY --from=builder /data /data
COPY --from=builder /etc/passwd /etc/passwd

USER data

VOLUME [ "/data" ]

CMD ["/go/bin/server"]
# ENTRYPOINT ["/entrypoint.sh"]