FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    freeradius \
    freeradius-postgresql \
    freeradius-rest \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create required directories and set permissions
RUN mkdir -p /var/run/freeradius /var/log/freeradius && \
    chown -R freerad:freerad /var/run/freeradius /var/log/freeradius

# Enable sql and rest modules (symlinks in versioned config dir)
RUN rm -f /etc/freeradius/3.0/mods-enabled/sql /etc/freeradius/3.0/mods-enabled/rest && \
    ln -s /etc/freeradius/3.0/mods-available/sql /etc/freeradius/3.0/mods-enabled/sql && \
    ln -s /etc/freeradius/3.0/mods-available/rest /etc/freeradius/3.0/mods-enabled/rest

# Config files at /etc/freeradius/3.0/ are mounted as volumes

EXPOSE 1812/udp 1813/udp

# Run as root to ensure log directory access, then drop privileges
CMD ["/usr/sbin/freeradius", "-f"]
