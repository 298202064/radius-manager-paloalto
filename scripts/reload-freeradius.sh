#!/bin/bash
# Reload FreeRADIUS configuration
# Usage: ./reload-freeradius.sh

set -e

echo "Reloading FreeRADIUS configuration..."

# Send SIGHUP to FreeRADIUS process
docker kill -s HUP radius-freeradius 2>/dev/null || \
  kill -HUP $(pgrep -f "radiusd") 2>/dev/null || \
  echo "Could not signal FreeRADIUS. Please reload manually."

echo "Done."
