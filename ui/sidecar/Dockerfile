# https://gallery.ecr.aws/docker/library/alpine
FROM public.ecr.aws/docker/library/alpine:3.19.1 as base

# Create a non-root user with a specified UID and GID
RUN addgroup --system --gid 50000 data \
  && adduser --system --uid 50000 --ingroup data data 

RUN mkdir /data \
  && chown data:data /data \
  && chmod 755 /data

# NOTE: Performing upgrade below to patch any outdated packages
RUN apk update \
  && apk add --no-cache bash curl aws-cli \
  && apk upgrade \
  && rm -rf /var/cache/apk/*

COPY entrypoint.sh /entrypoint.sh

# Remove unneeded packages for runtime
RUN apk del curl && apk cache clean

RUN chown data:data /entrypoint.sh \
  && chmod 700 /entrypoint.sh

# Set the working directory inside the container
WORKDIR /data

USER data

VOLUME [ "/data" ]

ENTRYPOINT ["/entrypoint.sh"]