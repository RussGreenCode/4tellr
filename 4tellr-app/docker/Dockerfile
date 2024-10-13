# Use the official MongoDB image from the Docker Hub
FROM mongo:latest

# Expose the default MongoDB port
EXPOSE 27017

# Create a volume to persist data
VOLUME /data/db

# Optionally, you can define environment variables for initial MongoDB setup
# These are optional and can be configured with your own credentials.
# Uncomment these lines if you want to pre-configure the database, username, and password.
#ENV MONGO_INITDB_ROOT_USERNAME=<
#ENV MONGO_INITDB_ROOT_PASSWORD=
ENV MONGO_INITDB_DATABASE=4tellr

# Default command to run MongoDB when the container starts
CMD ["mongod"]