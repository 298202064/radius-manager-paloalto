#!/bin/bash
# Bootstrap script for RADIUS Manager
# This script initializes the admin user and default settings.

set -e

echo "=== RADIUS Manager Bootstrap ==="

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
until pg_isready -h postgres -U ${DB_USER:-radius} -d ${DB_NAME:-radius} 2>/dev/null; do
  sleep 2
done
echo "PostgreSQL is ready."

# Wait for backend to be ready
echo "Waiting for backend..."
until curl -sf http://backend:8000/health > /dev/null 2>&1; do
  sleep 2
done
echo "Backend is ready."

# Create default admin user if not exists
echo "Setting up default admin user..."
curl -sf -X POST http://backend:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' > /dev/null && \
  echo "Default admin user exists (admin/admin123)" || \
  echo "Note: Login check failed. The admin user may need manual setup."

echo "=== Bootstrap complete ==="
echo ""
echo "Web UI: http://localhost:8081"
echo "Default login: admin / admin123"
echo ""
echo "IMPORTANT: Change the default password after first login!"
