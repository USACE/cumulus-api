# FROM pramsey/pg_featureserv:20241119
FROM ghcr.io/cwbi-apps/pg_featureserv:1.3.1-amd64

# Copy your entrypoint script into the container
COPY entrypoint.sh /entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["/entrypoint.sh"]

# Default command of pg_featureserv
CMD ["./pg_featureserv"]