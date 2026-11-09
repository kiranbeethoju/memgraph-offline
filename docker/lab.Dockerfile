# Memgraph Lab with Bolt quick-connect pointed at the Linux host.
# Start this image with --network host so 127.0.0.1:7687 is Memgraph,
# not an address inside the Lab container.
FROM memgraph/lab:latest

ENV QUICK_CONNECT_MG_HOST=127.0.0.1 \
    QUICK_CONNECT_MG_PORT=7687 \
    QUICK_CONNECT_MG_IS_ENCRYPTED=false \
    LOGIN_RESERVED_HOSTNAME_IS_ENABLED=true
