# BUILD GO BINARIES
FROM golang:1.19-alpine AS builder
# Install Git
RUN apk update && apk add --no-cache git ca-certificates
# Copy In Source Code
WORKDIR /go/src/app
COPY go.mod go.sum ./
# Install Dependencies
RUN go mod download && \
    go mod verify
# Build
COPY ./listener ./
RUN GOOS=linux GOARCH=amd64 CGO_ENABLED=0 \
    go build -ldflags="-w -s" -o /go/bin/cumulus-listener

# Create a "nobody" non-root user for the next image by crafting an /etc/passwd
# file that the next image can copy in. This is necessary since the next image
# is based on scratch, which doesn't have adduser, cat, echo, or even sh.
RUN echo "nobody:x:65534:65534:Nobody:/:" > /etc_passwd

# SCRATCH IMAGE
FROM scratch
COPY --from=builder /go/bin/cumulus-listener /go/bin/cumulus-listener
COPY --from=builder /etc/ssl/certs/ca-certificates.crt \
                    /etc/ssl/certs/ca-certificates.crt
COPY --from=builder /etc_passwd /etc/passwd

# Run as the new non-root by default
USER nobody

ENTRYPOINT ["/go/bin/cumulus-listener"]
