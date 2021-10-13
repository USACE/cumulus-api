FROM golang:1.15-alpine AS builder
# Install Git
RUN apk update && apk add --no-cache git
# Copy In Source Code
WORKDIR /go/src/app
COPY . .

# Install Dependencies
RUN go get -d -v
# Build
RUN go get -d -v \
  && GOOS=linux GOARCH=amd64 CGO_ENABLED=0 \
    go build -ldflags="-w -s" -o /go/bin/cumulus-api

# # SCRATCH IMAGE
FROM scratch
COPY --from=builder /go/bin/cumulus-api /go/bin/cumulus-api
COPY --from=builder /go/src/app/_sql /sql/
VOLUME [ "/sql" ]
ENTRYPOINT ["/go/bin/cumulus-api"]