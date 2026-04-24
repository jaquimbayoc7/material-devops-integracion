#!/bin/bash
set -e

# Dar acceso al socket de Docker al usuario jenkins
chmod 666 /var/run/docker.sock 2>/dev/null || true

# Ejecutar Jenkins como usuario jenkins (no como root)
exec gosu jenkins /usr/bin/tini -- /usr/local/bin/jenkins.sh "$@"
