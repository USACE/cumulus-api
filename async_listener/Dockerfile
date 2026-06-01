ARG GO_VERSION=1.26.3
ARG GO_TAG=${GO_VERSION}-alpine

# *~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~
# builder
# *~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~
FROM golang:${GO_TAG} AS builder
#
RUN apk update \
    && apk add --no-cache ca-certificates

# Copy In Source Code
WORKDIR /go/src/app

COPY ./listener go.mod go.sum ./

RUN go mod download \
    && go mod verify

# Build
#GOOS=linux GOARCH=amd64 CGO_ENABLED=0
RUN go build -ldflags="-w -s" -o /go/bin/cumulus-listener

# SCRATCH IMAGE
FROM scratch
COPY --from=builder /go/bin/cumulus-listener /go/bin/cumulus-listener
COPY --from=builder /etc/ssl/certs/ca-certificates.crt \
    /etc/ssl/certs/ca-certificates.crt
COPY --from=builder /etc/passwd /etc/passwd

# Run as the new non-root by default
USER nobody

ENTRYPOINT ["/go/bin/cumulus-listener"]
