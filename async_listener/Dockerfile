# BUILD GO BINARIES
FROM golang:1.14-alpine AS builder
# Install Git
RUN apk update && apk add --no-cache git ca-certificates
# Copy In Source Code
WORKDIR /go/src/app
COPY ./listener .
# Install Dependencies
RUN go get -d -v
# Build
RUN GOOS=linux GOARCH=amd64 CGO_ENABLED=0 \
    go build -ldflags="-w -s" -o /go/bin/cumulus-listener

# SCRATCH IMAGE
FROM scratch
COPY --from=builder /go/bin/cumulus-listener /go/bin/cumulus-listener
COPY --from=builder /etc/ssl/certs/ca-certificates.crt \
                    /etc/ssl/certs/ca-certificates.crt
ENTRYPOINT ["/go/bin/cumulus-listener"]
