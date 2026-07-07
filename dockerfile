# Start from the latest Arch Linux image
FROM archlinux:latest

# Set maintainer info
LABEL maintainer="brandon@admincraftsman.com"

# Update packages and install dependencies
RUN pacman -Syu --noconfirm && \
    pacman -S --noconfirm unzip curl jq screen

# Optional: clean up cached packages to keep image small
RUN pacman -Scc --noconfirm

# Create a non-root user
RUN useradd -m -d /home/minecraft -s /bin/bash minecraft

# Copy entrypoint as root
COPY entrypoint.sh /home/minecraft/entrypoint.sh
COPY fetch-server.sh /home/minecraft/fetch-server.sh
RUN chmod +x /home/minecraft/entrypoint.sh /home/minecraft/fetch-server.sh \
    && chown minecraft:minecraft /home/minecraft/entrypoint.sh /home/minecraft/fetch-server.sh

# Then switch to non-root user
USER minecraft
WORKDIR /home/minecraft

# Download the latest Bedrock server (change URL if needed)
RUN /home/minecraft/fetch-server.sh

# Accept EULA automatically
RUN echo "eula=true" > eula.txt

# Expose ports
EXPOSE 19132/udp
EXPOSE 19133/udp

ENTRYPOINT ["/home/minecraft/entrypoint.sh"]
CMD []