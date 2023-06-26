FROM golang:1.19-alpine AS builder
# Install Git
RUN apk update && apk add --no-cache ca-certificates
# Copy In Source Code
WORKDIR /go/src/app
COPY . .

# Install Dependencies
RUN go mod download && \
    go mod verify
# Build
RUN GOOS=linux GOARCH=amd64 CGO_ENABLED=0 \
    go build -ldflags="-w -s" -o /go/bin/cumulus-api

# # SCRATCH IMAGE
FROM scratch
COPY --from=builder /go/bin/cumulus-api /go/bin/cumulus-api
COPY --from=builder /etc/ssl/certs/ca-certificates.crt \
                    /etc/ssl/certs/ca-certificates.crt

VOLUME [ "/sql" ]
ENTRYPOINT ["/go/bin/cumulus-api"]