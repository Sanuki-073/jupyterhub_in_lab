# Dockerfile
# Base image
FROM jupyterhub/jupyterhub:3.1.1

# Install necessary packages and extensions
RUN apt-get update && \
    apt-get install -y docker.io && \
    pip install  jupyterhub-firstuseauthenticator==0.14.1\
                dockerspawner \
                docker


# Expose the port
EXPOSE 8000
