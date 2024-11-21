FROM pramsey/pg_featureserv:20241119

# Copy your entrypoint script into the container
COPY entrypoint.sh /entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["/entrypoint.sh"]

# Default command of pg_featureserv
CMD ["./pg_featureserv"]